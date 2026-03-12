import api from './api';
import type {
  Transaction,
  TransactionCreate,
  TransactionUpdate,
  TransactionFilters,
  PaginatedResponse,
  TransactionBulkUpdate,
  ImportPreview,
  ImportResult,
} from '@types';

const BASE_URL = '/transactions';

export const transactionApi = {
  // Get all transactions with filters
  getAll: async (filters?: TransactionFilters): Promise<PaginatedResponse<Transaction>> => {
    const response = await api.get(BASE_URL, { params: filters });
    return response.data;
  },

  // Get single transaction
  getById: async (id: string): Promise<Transaction> => {
    const response = await api.get(`${BASE_URL}/${id}`);
    return response.data.data;
  },

  // Create transaction
  create: async (data: TransactionCreate): Promise<Transaction> => {
    const response = await api.post(BASE_URL, data);
    return response.data.data;
  },

  // Update transaction
  update: async (id: string, data: TransactionUpdate): Promise<Transaction> => {
    const response = await api.patch(`${BASE_URL}/${id}`, data);
    return response.data.data;
  },

  // Delete transaction
  delete: async (id: string): Promise<void> => {
    await api.delete(`${BASE_URL}/${id}`);
  },

  // Bulk update
  bulkUpdate: async (data: TransactionBulkUpdate): Promise<Transaction[]> => {
    const response = await api.post(`${BASE_URL}/bulk`, data);
    return response.data.data;
  },

  // Validate transaction
  validate: async (id: string, categoryId: string): Promise<Transaction> => {
    const response = await api.post(`${BASE_URL}/${id}/validate`, { category_id: categoryId });
    return response.data.data;
  },

  // Import preview
  previewImport: async (file: File, accountId: string): Promise<ImportPreview> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('account_id', accountId);

    const response = await api.post(`${BASE_URL}/import/preview`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data.data;
  },

  // Confirm import
  confirmImport: async (transactions: TransactionCreate[]): Promise<ImportResult> => {
    const response = await api.post(`${BASE_URL}/import`, { transactions });
    return response.data.data;
  },

  // Get transaction stats
  getStats: async (accountId?: string) => {
    const response = await api.get(`${BASE_URL}/stats`, { params: { account_id: accountId } });
    return response.data.data;
  },
};
