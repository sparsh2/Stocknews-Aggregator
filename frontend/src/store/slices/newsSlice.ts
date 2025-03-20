import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import newsService, {
  NewsArticle,
  StockMention,
  ArticleCategory,
  NewsFilters,
  NewsResponse,
} from '../../services/api/news';
import { RootState } from '../index';

interface NewsState {
  articles: NewsArticle[];
  categories: ArticleCategory[];
  sources: string[];
  selectedArticle: NewsArticle | null;
  selectedStock: string | null;
  stockMentions: NewsArticle[];
  sentimentTrends: { date: string; sentiment_score: number }[];
  loading: boolean;
  error: string | null;
  total: number;
  page: number;
  pageSize: number;
}

const initialState: NewsState = {
  articles: [],
  categories: [],
  sources: [],
  selectedArticle: null,
  selectedStock: null,
  stockMentions: [],
  sentimentTrends: [],
  loading: false,
  error: null,
  total: 0,
  page: 1,
  pageSize: 10,
};

// Async thunks
export const fetchArticles = createAsyncThunk(
  'news/fetchArticles',
  async (filters: NewsFilters = {}, { rejectWithValue }) => {
    try {
      const response = await newsService.getArticles(filters);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch articles');
    }
  }
);

export const fetchArticle = createAsyncThunk(
  'news/fetchArticle',
  async (id: number, { rejectWithValue }) => {
    try {
      const article = await newsService.getArticle(id);
      return article;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch article');
    }
  }
);

export const fetchCategories = createAsyncThunk(
  'news/fetchCategories',
  async (_, { rejectWithValue }) => {
    try {
      const categories = await newsService.getCategories();
      return categories;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch categories');
    }
  }
);

export const fetchSources = createAsyncThunk(
  'news/fetchSources',
  async (_, { rejectWithValue }) => {
    try {
      const sources = await newsService.getSources();
      return sources;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch sources');
    }
  }
);

export const fetchStockMentions = createAsyncThunk(
  'news/fetchStockMentions',
  async (symbol: string, { rejectWithValue }) => {
    try {
      const mentions = await newsService.getStockMentions(symbol);
      return mentions;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch stock mentions');
    }
  }
);

export const fetchSentimentTrends = createAsyncThunk(
  'news/fetchSentimentTrends',
  async ({ symbol, days }: { symbol: string; days: number }, { rejectWithValue }) => {
    try {
      const trends = await newsService.getSentimentTrends(symbol, days);
      return trends;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch sentiment trends');
    }
  }
);

export const processArticle = createAsyncThunk(
  'news/processArticle',
  async (url: string, { rejectWithValue }) => {
    try {
      const article = await newsService.processArticle(url);
      return article;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to process article');
    }
  }
);

const newsSlice = createSlice({
  name: 'news',
  initialState,
  reducers: {
    setSelectedArticle: (state, action) => {
      state.selectedArticle = action.payload;
    },
    setSelectedStock: (state, action) => {
      state.selectedStock = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch Articles
      .addCase(fetchArticles.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchArticles.fulfilled, (state, action) => {
        state.loading = false;
        state.articles = action.payload.articles;
        state.total = action.payload.total;
        state.page = action.payload.page;
        state.pageSize = action.payload.page_size;
      })
      .addCase(fetchArticles.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // Fetch Article
      .addCase(fetchArticle.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchArticle.fulfilled, (state, action) => {
        state.loading = false;
        state.selectedArticle = action.payload;
      })
      .addCase(fetchArticle.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // Fetch Categories
      .addCase(fetchCategories.fulfilled, (state, action) => {
        state.categories = action.payload;
      })
      // Fetch Sources
      .addCase(fetchSources.fulfilled, (state, action) => {
        state.sources = action.payload;
      })
      // Fetch Stock Mentions
      .addCase(fetchStockMentions.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchStockMentions.fulfilled, (state, action) => {
        state.loading = false;
        state.stockMentions = action.payload;
      })
      .addCase(fetchStockMentions.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // Fetch Sentiment Trends
      .addCase(fetchSentimentTrends.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchSentimentTrends.fulfilled, (state, action) => {
        state.loading = false;
        state.sentimentTrends = action.payload;
      })
      .addCase(fetchSentimentTrends.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // Process Article
      .addCase(processArticle.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(processArticle.fulfilled, (state, action) => {
        state.loading = false;
        state.articles.unshift(action.payload);
        state.total += 1;
      })
      .addCase(processArticle.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const { setSelectedArticle, setSelectedStock, clearError } = newsSlice.actions;

// Selectors
export const selectArticles = (state: { news: NewsState }) => state.news.articles;
export const selectCategories = (state: { news: NewsState }) => state.news.categories;
export const selectSources = (state: { news: NewsState }) => state.news.sources;
export const selectSelectedArticle = (state: { news: NewsState }) => state.news.selectedArticle;
export const selectSelectedStock = (state: { news: NewsState }) => state.news.selectedStock;
export const selectStockMentions = (state: { news: NewsState }) => state.news.stockMentions;
export const selectSentimentTrends = (state: { news: NewsState }) => state.news.sentimentTrends;
export const selectLoading = (state: { news: NewsState }) => state.news.loading;
export const selectError = (state: { news: NewsState }) => state.news.error;
export const selectPagination = (state: { news: NewsState }) => ({
  total: state.news.total,
  page: state.news.page,
  pageSize: state.news.pageSize,
});

export default newsSlice.reducer; 