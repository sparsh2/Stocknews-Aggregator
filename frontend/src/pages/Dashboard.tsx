import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  LinearProgress,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  Article as ArticleIcon,
  Category as CategoryIcon,
  Timeline as TimelineIcon,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { RootState } from '../store';
import {
  fetchArticles,
  fetchCategories,
  selectArticles,
  selectCategories,
  selectLoading,
} from '../store/slices/newsSlice';

const Dashboard: React.FC = () => {
  const dispatch = useDispatch();
  const articles = useSelector(selectArticles);
  const categories = useSelector(selectCategories);
  const loading = useSelector(selectLoading);

  useEffect(() => {
    dispatch(fetchArticles());
    dispatch(fetchCategories());
  }, [dispatch]);

  const stats = {
    totalArticles: articles.length,
    totalCategories: categories.length,
    averageSentiment: articles.reduce((acc, article) => acc + (article.sentiment_score || 0), 0) / articles.length || 0,
    processedArticles: articles.filter(article => article.is_processed).length,
  };

  const sentimentData = articles
    .slice(-7)
    .map(article => ({
      date: new Date(article.published_at).toLocaleDateString(),
      sentiment: article.sentiment_score || 0,
    }));

  const StatCard: React.FC<{
    title: string;
    value: string | number;
    icon: React.ReactNode;
    color: string;
  }> = ({ title, value, icon, color }) => (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Box
            sx={{
              backgroundColor: `${color}20`,
              borderRadius: 1,
              p: 1,
              mr: 2,
            }}
          >
            {icon}
          </Box>
          <Typography variant="h6" component="div">
            {title}
          </Typography>
        </Box>
        <Typography variant="h4" component="div" sx={{ mb: 1 }}>
          {value}
        </Typography>
        <LinearProgress
          variant="determinate"
          value={100}
          sx={{ backgroundColor: `${color}20`, '& .MuiLinearProgress-bar': { backgroundColor: color } }}
        />
      </CardContent>
    </Card>
  );

  if (loading) {
    return <LinearProgress />;
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Articles"
            value={stats.totalArticles}
            icon={<ArticleIcon sx={{ color: '#1976d2' }} />}
            color="#1976d2"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Categories"
            value={stats.totalCategories}
            icon={<CategoryIcon sx={{ color: '#2e7d32' }} />}
            color="#2e7d32"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Avg. Sentiment"
            value={stats.averageSentiment.toFixed(2)}
            icon={<TrendingUpIcon sx={{ color: '#ed6c02' }} />}
            color="#ed6c02"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Processed"
            value={stats.processedArticles}
            icon={<TimelineIcon sx={{ color: '#9c27b0' }} />}
            color="#9c27b0"
          />
        </Grid>
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Sentiment Trend
            </Typography>
            <Box sx={{ height: 300 }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={sentimentData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Line
                    type="monotone"
                    dataKey="sentiment"
                    stroke="#1976d2"
                    strokeWidth={2}
                  />
                </LineChart>
              </ResponsiveContainer>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard; 