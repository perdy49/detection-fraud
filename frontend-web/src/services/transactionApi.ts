const API_BASE_URL = "http://127.0.0.1:8000";

export interface PredictionResponse {
  fraud_score: number;
  status: "FRAUD" | "SAFE";
}

export interface CsvPreviewResult {
  row: number;
  fraud_score: number;
  status: "FRAUD" | "SAFE";
}

export interface CsvPredictionResponse {
  total_transactions: number;
  fraud_count: number;
  safe_count: number;
  preview: CsvPreviewResult[];
}

export async function predictCsvFile(
  file: File,
): Promise<CsvPredictionResponse> {
  const formData = new FormData();

  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/api/transaction/predict-file`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);

    throw new Error(errorData?.detail || "Failed to analyze CSV file.");
  }

  return response.json();
}

export interface SingleTransactionRequest {
  amount: number;
  product_code: string;
  card_type: string;
  email: string;
  transaction_time: string;
}

export async function predictSingleTransaction(
  data: SingleTransactionRequest,
): Promise<PredictionResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/transaction/predict-single`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    },
  );

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);

    throw new Error(errorData?.detail || "Failed to predict transaction.");
  }

  return response.json();
}

export async function predictTransaction(
  features: number[],
): Promise<PredictionResponse> {
  const response = await fetch(`${API_BASE_URL}/api/transaction/predict`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      features,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);

    throw new Error(errorData?.detail || "Failed to predict transaction.");
  }

  return response.json();
}

export interface SaveHistoryRequest {
  amount: number;
  fraud_score: number;
  status: "FRAUD" | "SAFE";
  transaction_time: string;
}

export interface SaveHistoryResponse {
  message: string;
  data: {
    id: string;
    amount: number;
    fraud_score: number;
    status: "FRAUD" | "SAFE";
    transaction_time: string;
    created_at: string;
  };
}

export async function saveTransactionHistory(
  data: SaveHistoryRequest,
): Promise<SaveHistoryResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/transaction/history?amount=${encodeURIComponent(
      data.amount,
    )}&fraud_score=${encodeURIComponent(
      data.fraud_score,
    )}&status=${encodeURIComponent(
      data.status,
    )}&transaction_time=${encodeURIComponent(data.transaction_time)}`,
    {
      method: "POST",
    },
  );

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);

    throw new Error(errorData?.detail || "Failed to save transaction history.");
  }

  return response.json();
}