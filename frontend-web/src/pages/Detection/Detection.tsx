import { useRef, useState } from "react";
import "./Detection.css";
import useLanguage from "../../hooks/useLanguage";
import {
  predictSingleTransaction,
  predictCsvFile,
  type CsvPredictionResponse,
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
  file: File;
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

function getRecommendation(probability: number, t: ReturnType<typeof useLanguage>) {
  if (probability < 30) {
    return t.detection.recommendations.low;
  }

  if (probability < 60) {
    return t.detection.recommendations.medium;
  }

  if (probability < 80) {
    return t.detection.recommendations.high;
  }

  return t.detection.recommendations.critical;
}

function Detection() {
  const t = useLanguage();

  const [mode, setMode] = useState<"single" | "upload">("single");

  const [form, setForm] = useState<DetectionForm>({
    amount: "",
    productCode: "",
    cardType: "",
    email: "",
    transactionTime: getCurrentDateTime(),
  });

  const [result, setResult] = useState<DetectionResult | null>(null);

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [csvResult, setCsvResult] = useState<CsvPredictionResponse | null>(
    null,
  );

  const [csvFile, setCsvFile] = useState<CsvFile | null>(null);

  const [isDragging, setIsDragging] = useState(false);

  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const handleChange = (field: keyof DetectionForm, value: string) => {
    setForm((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  /*
   * =========================
   * SINGLE TRANSACTION
   * =========================
   */

  const handleAnalyze = async () => {
    if (!form.amount || !form.productCode || !form.cardType || !form.email) {
      alert(t.detection.messages.completeFields);
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
        transaction_time: form.transactionTime,
      });

      const probability = Number(response.fraud_score) * 100;

      setResult({
        status: response.status === "FRAUD" ? "Unauthorized" : "Legitimate",
        probability: Number(probability.toFixed(2)),
        recommendation: getRecommendation(probability, t),
      });
    } catch (error) {
      console.error("Single transaction prediction error:", error);

      alert(
        error instanceof Error
          ? error.message
          : t.detection.messages.singleError,
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

  const parseCsv = (text: string, file: File) => {
    const lines = text
      .split(/\r?\n/)
      .map((line) => line.trim())
      .filter(Boolean);

    if (lines.length === 0) {
      return;
    }

    const parseLine = (line: string) => {
      return line.split(",").map((value) => value.trim().replace(/^"|"$/g, ""));
    };

    const headers = parseLine(lines[0]);

    const rows = lines
      .slice(1)
      .map(parseLine)
      .filter((row) => row.length > 0);

    setCsvFile({
      file,
      name: file.name,
      size: file.size,
      headers,
      rows: rows.slice(0, 5),
      totalRows: rows.length,
    });
  };

  const handleFile = (file: File) => {
    if (!file.name.toLowerCase().endsWith(".csv")) {
      alert(t.detection.messages.csvOnly);
      return;
    }

    const reader = new FileReader();

    reader.onload = (event) => {
      const text = event.target?.result;

      if (typeof text !== "string") {
        return;
      }

      parseCsv(text, file);
    };

    reader.readAsText(file);
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    handleFile(file);
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();

    setIsDragging(false);

    const file = event.dataTransfer.files?.[0];

    if (!file) {
      return;
    }

    handleFile(file);
  };

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();

    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleChooseFile = () => {
    fileInputRef.current?.click();
  };

  const handleRemoveCsv = () => {
    setCsvFile(null);

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  /*
   * =========================
   * DOWNLOAD CSV SAMPLE
   * =========================
   */

  const handleDownloadSample = () => {
    const headers = [
      "TransactionID",
      "TransactionDT",
      "TransactionAmt",
      "ProductCD",
      "card1",
      "card2",
      "card3",
      "card4",
      "card5",
      "card6",
      "addr1",
      "addr2",
      "dist1",
      "dist2",
      "P_emaildomain",
      "R_emaildomain",

      ...Array.from({ length: 14 }, (_, i) => `C${i + 1}`),
      ...Array.from({ length: 15 }, (_, i) => `D${i + 1}`),
      ...Array.from({ length: 9 }, (_, i) => `M${i + 1}`),
      ...Array.from({ length: 339 }, (_, i) => `V${i + 1}`),
    ];

    const sampleRow = headers.map((header) => {
      switch (header) {
        case "TransactionID":
          return "1";

        case "TransactionDT":
          return "17280000";

        case "TransactionAmt":
          return "125.50";

        case "ProductCD":
          return "W";

        case "card1":
          return "10001";

        case "card2":
          return "123";

        case "card3":
          return "150";

        case "card4":
          return "visa";

        case "card5":
          return "226";

        case "card6":
          return "credit";

        case "addr1":
          return "315";

        case "addr2":
          return "87";

        case "dist1":
          return "10";

        case "dist2":
          return "5";

        case "P_emaildomain":
          return "gmail.com";

        case "R_emaildomain":
          return "gmail.com";

        default:
          return "";
      }
    });

    const csvContent = [headers.join(","), sampleRow.join(",")].join("\n");

    const blob = new Blob([csvContent], {
      type: "text/csv;charset=utf-8;",
    });

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
    if (!csvFile) {
      return;
    }

    setIsAnalyzing(true);
    setCsvResult(null);

    try {
      const response = await predictCsvFile(csvFile.file);

      setCsvResult(response);
    } catch (error) {
      console.error("CSV prediction error:", error);

      alert(
        error instanceof Error ? error.message : t.detection.messages.csvError,
      );
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
      transactionTime: getCurrentDateTime(),
    });
  };

  const handleSaveHistory = () => {
    /*
     * TODO:
     * Connect this to backend history API.
     */

    console.log("Save to history:", {
      form,
      result,
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
          {t.detection.modes.single}
        </button>

        <button
          className={`mode-btn ${mode === "upload" ? "active" : ""}`}
          onClick={() => setMode("upload")}
        >
          {t.detection.modes.upload}
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
              {isAnalyzing ? t.detection.actions.analyzing : t.detection.form.button}
            </button>
          </div>

          {/* RESULT */}

          <div className="prediction-panel">
            <h2>{t.detection.result.title}</h2>

            {!result ? (
              <div className="empty-result">
                <p>
                  {t.detection.result.emptyMessage}
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
                        width: `${result.probability}%`,
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
            <h2>{t.detection.upload.title}</h2>

            <p>
              {t.detection.upload.description}
            </p>
          </div>

          {/* DOWNLOAD SAMPLE */}

          <div className="csv-template-card">
            <div>
              <h3>{t.detection.upload.templateTitle}</h3>

              <p>
                {t.detection.upload.templateDescription}
              </p>
            </div>

            <button className="secondary-btn" onClick={handleDownloadSample}>
              {t.detection.upload.downloadSample}
            </button>
          </div>

          {/* UPLOAD AREA */}

          {!csvFile ? (
            <div
              className={`csv-upload-area ${isDragging ? "dragging" : ""}`}
              onClick={handleChooseFile}
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".csv,text/csv"
                onChange={handleFileChange}
                hidden
              />

              <div className="upload-icon">↑</div>

              <h3>{t.detection.upload.dropTitle}</h3>

              <p>{t.detection.upload.dropDescription}</p>

              <span>{t.detection.upload.supportedFormat}</span>
            </div>
          ) : (
            <>
              {/* FILE INFORMATION */}

              <div className="uploaded-file-card">
                <div className="uploaded-file-info">
                  <div className="file-icon">CSV</div>

                  <div>
                    <h3>{csvFile.name}</h3>

                    <p>{csvFile.totalRows} transactions detected</p>
                  </div>
                </div>

                <button className="remove-file-btn" onClick={handleRemoveCsv}>
                  Remove
                </button>
              </div>

              {/* CSV PREVIEW */}

              <div className="csv-preview">
                <div className="csv-preview-header">
                  <div>
                    <h3>{t.detection.upload.previewTitle}</h3>

                    <p>{t.detection.upload.previewDescription(csvFile.rows.length)}</p>
                  </div>

                  <span>{csvFile.headers.length} columns</span>
                </div>

                <div className="csv-table-wrapper">
                  <table>
                    <thead>
                      <tr>
                        {csvFile.headers.map((header, index) => (
                          <th key={`${header}-${index}`}>{header}</th>
                        ))}
                      </tr>
                    </thead>

                    <tbody>
                      {csvFile.rows.map((row, rowIndex) => (
                        <tr key={rowIndex}>
                          {csvFile.headers.map((_, columnIndex) => (
                            <td key={`${rowIndex}-${columnIndex}`}>
                              {row[columnIndex] || "-"}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* ANALYZE */}

              <button
                className="primary-btn upload-analyze-btn"
                onClick={handleAnalyzeCsv}
                disabled={isAnalyzing}
              >
                {isAnalyzing
                  ? t.detection.actions.analyzingTransactions
                  : t.detection.actions.analyzeTransactions}
              </button>

              {csvResult && (
                <section className="csv-result-section">
                  <div className="csv-result-header">
                    <div>
                      <span className="result-eyebrow">{t.detection.upload.completedEyebrow}</span>

                      <h2>{t.detection.upload.analysisResult}</h2>

                      <p>
                        {t.detection.upload.completedDescription}
                      </p>
                    </div>

                    <div className="result-completed-badge">{t.detection.upload.completed}</div>
                  </div>

                  <div className="csv-result-summary">
                    <div className="csv-result-item total">
                      <span>{t.detection.upload.totalTransactions}</span>

                      <strong>
                        {csvResult.total_transactions.toLocaleString()}
                      </strong>
                    </div>

                    <div className="csv-result-item fraud">
                      <span>{t.detection.upload.fraudDetected}</span>

                      <strong>{csvResult.fraud_count.toLocaleString()}</strong>
                    </div>

                    <div className="csv-result-item safe">
                      <span>{t.detection.upload.safeTransactions}</span>

                      <strong>{csvResult.safe_count.toLocaleString()}</strong>
                    </div>
                  </div>

                  <div className="detection-overview">
                    <div className="overview-header">
                      <h3>{t.detection.upload.detectionOverview}</h3>

                      <span>
                        {(
                          (csvResult.fraud_count /
                            csvResult.total_transactions) *
                          100
                        ).toFixed(2)}
                        {t.detection.upload.fraudRate}
                      </span>
                    </div>

                    <div className="overview-bar">
                      <div
                        className="overview-fraud"
                        style={{
                          width: `${
                            (csvResult.fraud_count /
                              csvResult.total_transactions) *
                            100
                          }%`,
                        }}
                      />
                    </div>

                    <div className="overview-legend">
                      <span>
                        <i className="legend-dot fraud-dot" />
                        {t.detection.upload.fraud}: {csvResult.fraud_count.toLocaleString()}
                      </span>

                      <span>
                        <i className="legend-dot safe-dot" />
                        {t.detection.upload.safe}: {csvResult.safe_count.toLocaleString()}
                      </span>
                    </div>
                  </div>

                  <div className="csv-preview-result">
                    <div className="prediction-header">
                      <div>
                        <h3>{t.detection.upload.predictionDetails}</h3>

                        <p>
                          {t.detection.upload.predictionDescription}
                        </p>
                      </div>

                      <span className="preview-count">
                        {csvResult.preview.length} results
                      </span>
                    </div>

                    <div className="prediction-table-scroll">
                      <table>
                        <thead>
                          <tr>
                            <th>{t.detection.upload.row}</th>
                            <th>{t.detection.upload.fraudScore}</th>
                            <th>{t.detection.result.status}</th>
                          </tr>
                        </thead>

                        <tbody>
                          {csvResult.preview.map((item) => (
                            <tr key={item.row}>
                              <td>{item.row}</td>

                              <td>
                                <div className="fraud-score">
                                  <div className="score-bar">
                                    <div
                                      className={
                                        item.status === "FRAUD"
                                          ? "score-fill danger"
                                          : "score-fill safe"
                                      }
                                      style={{
                                        width: `${item.fraud_score * 100}%`,
                                      }}
                                    />
                                  </div>

                                  <span>
                                    {(item.fraud_score * 100).toFixed(2)}%
                                  </span>
                                </div>
                              </td>

                              <td>
                                <span
                                  className={
                                    item.status === "FRAUD"
                                      ? "csv-danger-status"
                                      : "csv-safe-status"
                                  }
                                >
                                  <span className="status-dot" />

                                  {item.status === "FRAUD"
                                    ? t.detection.status.fraud
                                    : t.detection.status.safe}
                                </span>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </section>
              )}
            </>
          )}
        </section>
      )}
    </div>
  );
}

export default Detection;
