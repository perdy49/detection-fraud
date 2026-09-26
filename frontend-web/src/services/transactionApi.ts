const API_BASE_URL = "http://127.0.0.1:8000";

export interface PredictionResponse {
  fraud_score: number;
  status: "FRAUD" | "SAFE";
}

export interface SingleTransactionRequest {
  amount: number;
  product_code: string;
  card_type: string;
  email: string;
  transaction_time: string;
}

export async function predictSingleTransaction(
  data: SingleTransactionRequest
): Promise<PredictionResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/transaction/predict-single`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(data)
    }
  );

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);

    throw new Error(errorData?.detail || "Failed to predict transaction.");
  }

  return response.json();
}

export async function predictTransaction(
  features: number[]
): Promise<PredictionResponse> {
  const response = await fetch(`${API_BASE_URL}/api/transaction/predict`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      features
    })
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);

    throw new Error(errorData?.detail || "Failed to predict transaction.");
  }

  return response.json();
}

export interface CsvAnalysisStatus {
  job_id: string;
  status: "queued" | "processing" | "completed" | "failed";
  progress: number;
  processed_rows?: number;
  total_rows?: number;
  message?: string;
  result?: {
    total_transactions: number;
    safe_transactions: number;
    fraud_transactions: number;
    fraud_percentage: number;
    average_fraud_score: number;
    highest_risk: Array<{
      transaction_id: string | number;
      fraud_score: number;
      status: "SAFE" | "FRAUD";
    }>;
  };
}

export async function analyzeCsv(
  transactionFile: File,
  identityFile?: File
): Promise<{ job_id: string; status: string }> {
  const formData = new FormData();

  formData.append("transaction_file", transactionFile);

  if (identityFile) {
    formData.append("identity_file", identityFile);
  }

  const response = await fetch(
    `${API_BASE_URL}/api/transaction/analyze-csv`,
    {
      method: "POST",
      body: formData
    }
  );

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    throw new Error(
      errorData?.detail || "Failed to start CSV analysis."
    );
  }

  return response.json();
}

export async function getCsvAnalysis(
  jobId: string
): Promise<CsvAnalysisStatus> {
  const response = await fetch(
    `${API_BASE_URL}/api/transaction/analyze-csv/${jobId}`
  );

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    throw new Error(
      errorData?.detail || "Failed to get CSV analysis status."
    );
  }

  return response.json();
}

export function getCsvAnalysisDownloadUrl(jobId: string) {
  return `${API_BASE_URL}/api/transaction/analyze-csv/${jobId}/download`;
}
