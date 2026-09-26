import { useRef, useState } from "react";
import "./Detection.css";
import useLanguage from "../../hooks/useLanguage";
import {
  analyzeCsv,
  getCsvAnalysis,
  getCsvAnalysisDownloadUrl,
  predictSingleTransaction,
  type CsvAnalysisStatus
} from "../../services/transactionApi";

interface DetectionForm {
  amount: string;
  productCode: string;
  cardType: string;
  email: string;
  transactionTime: string;
}

interface DetectionResult {
  status: "Legitimate" | "Unauthorized";
  probability: number;
  recommendation: string;
}

interface CsvFile {
  name: string;
  size: number;
  headers: string[];
  rows: string[][];
  totalRows: number;
}

function getCurrentDateTime() {
  const now = new Date();

  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  const hours = String(now.getHours()).padStart(2, "0");
  const minutes = String(now.getMinutes()).padStart(2, "0");

  return `${year}-${month}-${day}T${hours}:${minutes}`;
}

function getRecommendation(probability: number) {
  if (probability < 30) {
    return "This transaction appears legitimate. No significant unauthorized activity was detected.";
  }

  if (probability < 60) {
    return "This transaction shows some suspicious characteristics. Additional verification is recommended.";
  }

  if (probability < 80) {
    return "This transaction shows a high risk of unauthorized activity. Please verify the transaction before proceeding.";
  }

  return "This transaction is highly suspicious. Additional verification is strongly recommended before proceeding.";
}

function Detection() {
  const t = useLanguage();

  const [mode, setMode] = useState<"single" | "upload">("single");

  const [form, setForm] = useState<DetectionForm>({
    amount: "",
    productCode: "",
    cardType: "",
    email: "",
    transactionTime: getCurrentDateTime()
  });

  const [result, setResult] = useState<DetectionResult | null>(null);

  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleChange = (field: keyof DetectionForm, value: string) => {
    setForm((prev) => ({
      ...prev,
      [field]: value
    }));
  };

  /*
   * =========================
   * SINGLE TRANSACTION
   * =========================
   */

  const handleAnalyze = async () => {
    if (!form.amount || !form.productCode || !form.cardType || !form.email) {
      return;
    }

    setIsAnalyzing(true);
    setResult(null);

    try {
      const response = await predictSingleTransaction({
        amount: Number(form.amount),
        product_code: form.productCode,
        card_type: form.cardType,
        email: form.email,
        transaction_time: form.transactionTime
      });

      const probability = response.fraud_score * 100;

      setResult({
        status: response.status === "FRAUD" ? "Unauthorized" : "Legitimate",

        probability,

        recommendation: getRecommendation(probability)
      });
    } catch (error) {
      console.error("Prediction error:", error);

      alert(
        error instanceof Error
          ? error.message
          : "Failed to analyze transaction."
      );
    } finally {
      setIsAnalyzing(false);
    }
  };

  /*
   * =========================
   * CSV UPLOAD
   * =========================
   */

  const [csvFile, setCsvFile] = useState<CsvFile | null>(null);
  const [identityFile, setIdentityFile] = useState<File | null>(null);
  const [csvAnalysis, setCsvAnalysis] = useState<CsvAnalysisStatus["result"] | null>(null);
  const [csvProgress, setCsvProgress] = useState(0);
  const [csvMessage, setCsvMessage] = useState("");
  const [csvJobId, setCsvJobId] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const identityInputRef = useRef<HTMLInputElement | null>(null);

  const parseCsvPreview = (text: string, fileName: string, fileSize: number) => {
    const lines = text.split(/\r?\n/).map((line) => line.trim()).filter(Boolean).slice(0, 6);
    if (lines.length === 0) throw new Error("CSV file is empty.");
    const parseLine = (line: string) => line.split(",").map((value) => value.trim().replace(/^"|"$/g, ""));
    const headers = parseLine(lines[0]);
    const rows = lines.slice(1).map(parseLine);
    if (!headers.includes("TransactionID")) throw new Error("Transaction CSV must contain a TransactionID column.");
    setCsvFile({ name: fileName, size: fileSize, headers, rows: rows.slice(0, 5), totalRows: 0 });
  };

  const handleFile = (file: File) => {
    if (!file.name.toLowerCase().endsWith(".csv")) {
      alert("Please upload a CSV file.");
      return;
    }
    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target?.result;
      if (typeof text !== "string") return;
      try {
        parseCsvPreview(text, file.name, file.size);
        setCsvAnalysis(null);
        setCsvProgress(0);
        setCsvMessage("");
        setCsvJobId(null);
      } catch (error) {
        alert(error instanceof Error ? error.message : "Invalid CSV file.");
      }
    };
    reader.readAsText(file.slice(0, Math.min(file.size, 1024 * 1024)));
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) handleFile(file);
  };

  const handleIdentityChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    if (!file.name.toLowerCase().endsWith(".csv")) {
      alert("Identity file must be a CSV.");
      return;
    }
    setIdentityFile(file);
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(false);
    const file = event.dataTransfer.files?.[0];
    if (file) handleFile(file);
  };

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => setIsDragging(false);
  const handleChooseFile = () => fileInputRef.current?.click();

  const handleRemoveCsv = () => {
    setCsvFile(null);
    setIdentityFile(null);
    setCsvAnalysis(null);
    setCsvProgress(0);
    setCsvMessage("");
    setCsvJobId(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
    if (identityInputRef.current) identityInputRef.current.value = "";
  };

  /*
   * =========================
   * DOWNLOAD CSV SAMPLE
   * =========================
   */

  const handleDownloadSample = () => {
    const headers = [
      "TransactionID", "TransactionDT", "TransactionAmt", "ProductCD",
      "card1", "card2", "card3", "card4", "card5", "card6",
      "addr1", "addr2", "dist1", "dist2", "P_emaildomain", "R_emaildomain",
      ...Array.from({ length: 14 }, (_, i) => `C${i + 1}`),
      ...Array.from({ length: 15 }, (_, i) => `D${i + 1}`),
      ...Array.from({ length: 9 }, (_, i) => `M${i + 1}`),
      ...Array.from({ length: 339 }, (_, i) => `V${i + 1}`)
    ];

    const sampleRow = headers.map((header) => {
      switch (header) {
        case "TransactionID": return "1";
        case "TransactionDT": return "17280000";
        case "TransactionAmt": return "125.50";
        case "ProductCD": return "W";
        case "card1": return "10001";
        case "card2": return "123";
        case "card3": return "150";
        case "card4": return "visa";
        case "card5": return "226";
        case "card6": return "credit";
        case "addr1": return "315";
        case "addr2": return "87";
        case "dist1": return "10";
        case "dist2": return "5";
        case "P_emaildomain": return "gmail.com";
        case "R_emaildomain": return "gmail.com";
        default: return "";
      }
    });

    const csvContent = [headers.join(","), sampleRow.join("\n")].join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "transaction_sample.csv";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  /*
   * =========================
   * CSV ANALYZE
   * =========================
   */

  const handleAnalyzeCsv = async () => {
    if (!csvFile) return;
    const transactionFile = fileInputRef.current?.files?.[0];
    if (!transactionFile) {
      alert("Please select the transaction CSV again.");
      return;
    }

    setIsAnalyzing(true);
    setCsvAnalysis(null);
    setCsvProgress(1);
    setCsvMessage("Uploading CSV...");

    try {
      const started = await analyzeCsv(transactionFile, identityFile || undefined);
      setCsvJobId(started.job_id);

      let finished = false;
      while (!finished) {
        const status = await getCsvAnalysis(started.job_id);
        setCsvProgress(status.progress || 0);
        setCsvMessage(status.message || "Analyzing transactions...");

        if (status.status === "completed") {
          setCsvAnalysis(status.result || null);
          finished = true;
        }
        if (status.status === "failed") {
          throw new Error(status.message || "CSV analysis failed.");
        }
        if (!finished) await new Promise((resolve) => setTimeout(resolve, 1000));
      }
      setCsvMessage("Analysis completed.");
    } catch (error) {
      console.error("CSV analysis error:", error);
      alert(error instanceof Error ? error.message : "Failed to analyze CSV.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  /*
   * =========================
   * CLEAR
   * =========================
   */

  const handleClear = () => {
    setResult(null);

    setForm({
      amount: "",
      productCode: "",
      cardType: "",
      email: "",
      transactionTime: getCurrentDateTime()
    });
  };

  const handleSaveHistory = () => {
    /*
     * TODO:
     * Connect this to backend history API.
     */

    console.log("Save to history:", {
      form,
      result
    });
  };

  return (
    <div className="detection">
      <section className="detection-header">
        <h1>{t.detection.title}</h1>

        <p>{t.detection.description}</p>
      </section>

      {/* =========================
          DETECTION MODE
      ========================== */}

      <section className="detection-mode">
        <button
          className={`mode-btn ${mode === "single" ? "active" : ""}`}
          onClick={() => setMode("single")}
        >
          Single Transaction
        </button>

        <button
          className={`mode-btn ${mode === "upload" ? "active" : ""}`}
          onClick={() => setMode("upload")}
        >
          Upload Transaction File
        </button>
      </section>

      {/* =========================
          SINGLE TRANSACTION MODE
      ========================== */}

      {mode === "single" && (
        <section className="detection-container">
          <div className="detection-form">
            <h2>{t.detection.form.title}</h2>

            <div className="form-group">
              <label>{t.detection.form.amount}</label>

              <input
                type="number"
                min="0"
                step="0.01"
                value={form.amount}
                placeholder={t.detection.form.amountPlaceholder}
                onChange={(e) => handleChange("amount", e.target.value)}
              />
            </div>

            <div className="form-group">
              <label>{t.detection.form.product}</label>

              <select
                value={form.productCode}
                onChange={(e) => handleChange("productCode", e.target.value)}
              >
                <option value="" disabled>
                  {t.detection.form.productPlaceholder}
                </option>

                <option value="W">W</option>
                <option value="H">H</option>
                <option value="C">C</option>
                <option value="S">S</option>
                <option value="R">R</option>
              </select>
            </div>

            <div className="form-group">
              <label>{t.detection.form.card}</label>

              <select
                value={form.cardType}
                onChange={(e) => handleChange("cardType", e.target.value)}
              >
                <option value="" disabled>
                  {t.detection.form.cardPlaceholder}
                </option>

                <option value="visa">Visa</option>
                <option value="mastercard">Mastercard</option>
                <option value="discover">Discover</option>
                <option value="american express">American Express</option>
              </select>
            </div>

            <div className="form-group">
              <label>{t.detection.form.email}</label>

              <input
                type="email"
                value={form.email}
                placeholder={t.detection.form.emailPlaceholder}
                onChange={(e) => handleChange("email", e.target.value)}
              />
            </div>

            <div className="form-group">
              <label>{t.detection.form.time}</label>

              <input
                type="datetime-local"
                value={form.transactionTime}
                readOnly
              />
            </div>

            <button
              className="primary-btn"
              onClick={handleAnalyze}
              disabled={isAnalyzing}
            >
              {isAnalyzing ? "Analyzing..." : t.detection.form.button}
            </button>
          </div>

          {/* RESULT */}

          <div className="prediction-panel">
            <h2>{t.detection.result.title}</h2>

            {!result ? (
              <div className="empty-result">
                <p>
                  Enter transaction information and click
                  <strong> Analyze Transaction </strong>
                  to see the detection result.
                </p>
              </div>
            ) : (
              <>
                <div className="result-card">
                  <h3>{t.detection.result.status}</h3>

                  <span
                    className={
                      result.status === "Legitimate"
                        ? "safe-status"
                        : "danger-status"
                    }
                  >
                    {result.status}
                  </span>
                </div>

                <div className="result-card">
                  <h3>{t.detection.result.probability}</h3>

                  <div className="progress">
                    <div
                      className={
                        result.status === "Legitimate"
                          ? "progress-fill safe"
                          : "progress-fill danger"
                      }
                      style={{
                        width: `${result.probability}%`
                      }}
                    />
                  </div>

                  <p>{result.probability}%</p>
                </div>

                <div className="result-card">
                  <h3>{t.detection.result.recommendation}</h3>

                  <p>{result.recommendation}</p>
                </div>

                <div className="result-actions">
                  <button className="delete-result-btn" onClick={handleClear}>
                    {t.detection.result.ClearResults}
                  </button>

                  <button
                    className="save-result-btn"
                    onClick={handleSaveHistory}
                  >
                    {t.detection.result.SaveToHistory}
                  </button>
                </div>
              </>
            )}
          </div>
        </section>
      )}

      {/* =========================
          UPLOAD CSV MODE
      ========================== */}

      {mode === "upload" && (
        <section className="upload-container">
          <div className="upload-header">
            <h2>Upload Transaction File</h2>
            <p>Upload a transaction CSV for AI analysis. Large files are processed on the backend in batches.</p>
          </div>
          <div className="csv-template-card">
            <div>
              <h3>CSV Template</h3>
              <p>Transaction CSV is required. Identity CSV is optional and is merged using TransactionID.</p>
            </div>
            <button className="secondary-btn" onClick={handleDownloadSample}>Download CSV Sample</button>
          </div>

          {!csvFile ? (
            <div
              className={`csv-upload-area ${isDragging ? "dragging" : ""}`}
              onClick={handleChooseFile}
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
            >
              <input ref={fileInputRef} type="file" accept=".csv,text/csv" onChange={handleFileChange} hidden />
              <div className="upload-icon">↑</div>
              <h3>Drop your transaction CSV here</h3>
              <p>or click to browse from your computer</p>
              <span>Large files are not loaded into browser memory</span>
            </div>
          ) : (
            <>
              <div className="uploaded-file-card">
                <div className="uploaded-file-info">
                  <div className="file-icon">CSV</div>
                  <div>
                    <h3>{csvFile.name}</h3>
                    <p>
                      {csvFile.size >= 1024 * 1024
                        ? `${(csvFile.size / 1024 / 1024).toFixed(1)} MB`
                        : `${(csvFile.size / 1024).toFixed(1)} KB`}
                      {" · transaction CSV selected"}
                    </p>
                  </div>
                </div>
                <button className="remove-file-btn" onClick={handleRemoveCsv}>Remove</button>
              </div>

              <div className="csv-template-card">
                <div>
                  <h3>Identity CSV <span>(optional)</span></h3>
                  <p>For IEEE-CIS data, select the matching identity CSV.</p>
                  {identityFile && <p>Selected: <strong>{identityFile.name}</strong></p>}
                </div>
                <input ref={identityInputRef} type="file" accept=".csv,text/csv" onChange={handleIdentityChange} hidden />
                <button className="secondary-btn" onClick={() => identityInputRef.current?.click()}>
                  {identityFile ? "Change Identity CSV" : "Choose Identity CSV"}
                </button>
              </div>

              <div className="csv-preview">
                <div className="csv-preview-header">
                  <div>
                    <h3>CSV Preview</h3>
                    <p>Showing the first {csvFile.rows.length} rows</p>
                  </div>
                  <span>{csvFile.headers.length} columns</span>
                </div>
                <div className="csv-table-wrapper">
                  <table>
                    <thead>
                      <tr>{csvFile.headers.map((header, index) => <th key={`${header}-${index}`}>{header}</th>)}</tr>
                    </thead>
                    <tbody>
                      {csvFile.rows.map((row, rowIndex) => (
                        <tr key={rowIndex}>
                          {csvFile.headers.map((_, columnIndex) => (
                            <td key={`${rowIndex}-${columnIndex}`}>{row[columnIndex] || "-"}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {isAnalyzing && (
                <div className="result-card">
                  <h3>AI Analysis Progress</h3>
                  <div className="progress">
                    <div className="progress-fill safe" style={{ width: `${csvProgress}%` }} />
                  </div>
                  <p>{csvProgress}% — {csvMessage}</p>
                </div>
              )}

              {csvAnalysis && (
                <>
                  <div className="result-card">
                    <h3>Analysis Result</h3>
                    <p>Total transactions: <strong>{csvAnalysis.total_transactions.toLocaleString()}</strong></p>
                    <p>SAFE: <strong>{csvAnalysis.safe_transactions.toLocaleString()}</strong></p>
                    <p>FRAUD: <strong>{csvAnalysis.fraud_transactions.toLocaleString()}</strong></p>
                    <p>Fraud percentage: <strong>{csvAnalysis.fraud_percentage.toFixed(2)}%</strong></p>
                    <p>Average fraud score: <strong>{(csvAnalysis.average_fraud_score * 100).toFixed(2)}%</strong></p>
                  </div>

                  <div className="result-card">
                    <h3>Highest Risk Transactions</h3>
                    {csvAnalysis.highest_risk.map((item, index) => (
                      <p key={`${item.transaction_id}-${index}`}>
                        #{index + 1} — Transaction <strong>{item.transaction_id}</strong> — {(item.fraud_score * 100).toFixed(2)}% — <strong>{item.status}</strong>
                      </p>
                    ))}
                  </div>

                  {csvJobId && (
                    <button className="secondary-btn" onClick={() => window.open(getCsvAnalysisDownloadUrl(csvJobId), "_blank")}>
                      Download Full Analysis CSV
                    </button>
                  )}
                </>
              )}

              <button className="primary-btn upload-analyze-btn" onClick={handleAnalyzeCsv} disabled={isAnalyzing}>
                {isAnalyzing ? "Analyzing Transactions..." : csvAnalysis ? "Analyze Again" : "Analyze Transactions"}
              </button>
            </>
          )}
        </section>
      )}}
    </div>
  );
}

export default Detection;
