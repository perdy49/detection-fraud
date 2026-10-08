import { useEffect, useState } from "react";
import "./History.css";
import useLanguage from "../../hooks/useLanguage";

const API_BASE_URL = "http://127.0.0.1:8000";

interface HistoryItem {
  id: string;
  amount: number;
  fraud_score: number;
  status: "SAFE" | "FRAUD";
  transaction_time: string;
  created_at: string;
}

interface HistoryResponse {
  total: number;
  data: HistoryItem[];
}

function History() {
  const t = useLanguage();

  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("ALL");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadHistory = async () => {
      try {
        setLoading(true);
        setError("");

        const params = new URLSearchParams();

        if (search.trim()) {
          params.append("search", search.trim());
        }

        if (status !== "ALL") {
          params.append("status", status);
        }

        const query = params.toString();

        const response = await fetch(
          `${API_BASE_URL}/api/transaction/history${query ? `?${query}` : ""}`,
        );

        if (!response.ok) {
          const errorData = await response.json().catch(() => null);

          throw new Error(
            errorData?.detail || "Failed to load transaction history.",
          );
        }

        const result: HistoryResponse = await response.json();

        setHistory(result.data);
      } catch (err) {
        setHistory([]);

        setError(
          err instanceof Error
            ? err.message
            : "Failed to load transaction history.",
        );
      } finally {
        setLoading(false);
      }
    };

    const timer = setTimeout(() => {
      loadHistory();
    }, 300);

    return () => {
      clearTimeout(timer);
    };
  }, [search, status]);

  const formatAmount = (amount: number) => {
    return `Rp ${amount.toLocaleString("id-ID")}`;
  };

  const formatProbability = (score: number) => {
    return `${(score * 100).toFixed(0)}%`;
  };

  const formatDate = (date: string) => {
    const parsedDate = new Date(date);

    if (Number.isNaN(parsedDate.getTime())) {
      return date;
    }

    return parsedDate.toLocaleDateString("id-ID", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    });
  };

  const handleDelete = async (transactionId: string) => {
    const confirmed = window.confirm(
      "Are you sure you want to delete this transaction?",
    );

    if (!confirmed) {
      return;
    }

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/transaction/history/${transactionId}`,
        {
          method: "DELETE",
        },
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);

        throw new Error(errorData?.detail || "Failed to delete transaction.");
      }

      setHistory((currentHistory) =>
        currentHistory.filter((item) => item.id !== transactionId),
      );
    } catch (err) {
      window.alert(
        err instanceof Error ? err.message : "Failed to delete transaction.",
      );
    }
  };

  return (
    <div className="history">
      <section className="history-header">
        <h1>{t.history.title}</h1>

        <p>{t.history.description}</p>
      </section>

      <section className="history-search">
        <input
          type="text"
          value={search}
          onChange={(event) => {
            setSearch(event.target.value);
          }}
          placeholder={t.history.search}
        />

        <select
          value={status}
          onChange={(event) => {
            setStatus(event.target.value);
          }}
        >
          <option value="ALL">{t.history.filter.all}</option>

          <option value="SAFE">{t.history.filter.legitimate}</option>

          <option value="FRAUD">{t.history.filter.unauthorized}</option>
        </select>
      </section>

      <section className="history-list">
        {loading && (
          <div className="history-empty">
            <p>Loading...</p>
          </div>
        )}

        {!loading && error && (
          <div className="history-empty">
            <p>{error}</p>
          </div>
        )}

        {!loading && !error && history.length === 0 && (
          <div className="history-empty">
            <p>
              {search.trim() || status !== "ALL"
                ? "No transactions found."
                : "No transaction history yet."}
            </p>
          </div>
        )}

        {!loading &&
          !error &&
          history.map((item) => (
            <div className="history-card" key={item.id}>
              <div className="history-top">
                <h3>#{item.id}</h3>

                <span className={item.status === "SAFE" ? "safe" : "fraud"}>
                  {item.status === "SAFE"
                    ? t.history.filter.legitimate
                    : t.history.filter.unauthorized}
                </span>
              </div>

              <div className="history-body">
                <div>
                  <label>{t.history.amount}</label>

                  <p>{formatAmount(item.amount)}</p>
                </div>

                <div>
                  <label>{t.history.probability}</label>

                  <p>{formatProbability(item.fraud_score)}</p>
                </div>

                <div>
                  <label>{t.history.date}</label>

                  <p>{formatDate(item.transaction_time)}</p>
                </div>
              </div>

              <div className="history-card-actions">
                <button
                  type="button"
                  className="delete-history-btn"
                  onClick={() => handleDelete(item.id)}
                >
                  Hapus
                </button>
              </div>
            </div>
          ))}
      </section>
    </div>
  );
}

export default History;
