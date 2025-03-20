import api from './config';

export interface NewsArticle {
  id: number;
  title: string;
  content: string;
  url: string;
  source: string;
  published_at: string;
  sentiment_score: number;
  stock_mentions: StockMention[];
  categories: ArticleCategory[];
}

export interface StockMention {
  id: number;
  symbol: string;
  sentiment_score: number;
  relevance_score: number;
}

export interface ArticleCategory {
  id: number;
  name: string;
  description: string;
}

export interface NewsFilters {
  search?: string;
  categories?: number[];
  sources?: string[];
  start_date?: string;
  end_date?: string;
  sentiment_range?: [number, number];
  page?: number;
  page_size?: number;
}

export interface NewsResponse {
  articles: NewsArticle[];
  total: number;
  page: number;
  page_size: number;
}

const newsService = {
  getArticles: async (filters: NewsFilters = {}): Promise<NewsResponse> => {
    const response = await api.get<NewsResponse>('/news/articles', { params: filters });
    return response.data;
  },

  getArticle: async (id: number): Promise<NewsArticle> => {
    const response = await api.get<NewsArticle>(`/news/articles/${id}`);
    return response.data;
  },

  getCategories: async (): Promise<ArticleCategory[]> => {
    const response = await api.get<ArticleCategory[]>('/news/categories');
    return response.data;
  },

  getSources: async (): Promise<string[]> => {
    const response = await api.get<string[]>('/news/sources');
    return response.data;
  },

  getStockMentions: async (symbol: string): Promise<NewsArticle[]> => {
    const response = await api.get<NewsArticle[]>(`/news/stocks/${symbol}/mentions`);
    return response.data;
  },

  getSentimentTrends: async (symbol: string, days: number = 30): Promise<{
    date: string;
    sentiment_score: number;
  }[]> => {
    const response = await api.get(`/news/stocks/${symbol}/sentiment-trends`, {
      params: { days },
    });
    return response.data;
  },

  processArticle: async (url: string): Promise<NewsArticle> => {
    const response = await api.post<NewsArticle>('/news/process', { url });
    return response.data;
  },
};

export default newsService; 