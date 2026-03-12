import api from './api';
import type {
  Category,
  CategoryCreate,
  CategoryUpdate,
  CategoryWithStats,
} from '@types';

const BASE_URL = '/categories';

export const categoryApi = {
  // Get all categories
  getAll: async (): Promise<Category[]> => {
    const response = await api.get(BASE_URL);
    return response.data.data;
  },

  // Get category tree
  getTree: async (): Promise<Category[]> => {
    const response = await api.get(`${BASE_URL}/tree`);
    return response.data.data;
  },

  // Get category with stats
  getWithStats: async (): Promise<CategoryWithStats[]> => {
    const response = await api.get(`${BASE_URL}/stats`);
    return response.data.data;
  },

  // Get single category
  getById: async (id: string): Promise<Category> => {
    const response = await api.get(`${BASE_URL}/${id}`);
    return response.data.data;
  },

  // Create category
  create: async (data: CategoryCreate): Promise<Category> => {
    const response = await api.post(BASE_URL, data);
    return response.data.data;
  },

  // Update category
  update: async (id: string, data: CategoryUpdate): Promise<Category> => {
    const response = await api.patch(`${BASE_URL}/${id}`, data);
    return response.data.data;
  },

  // Delete category
  delete: async (id: string): Promise<void> => {
    await api.delete(`${BASE_URL}/${id}`);
  },
};
