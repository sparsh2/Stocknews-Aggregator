import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Box,
  Typography,
  Paper,
  Grid,
  TextField,
  Autocomplete,
  LinearProgress,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from 'recharts';
import { RootState } from '../store';
import {
  fetchArticles,
  selectArticles,
  selectNewsLoading,
} from '../store/slices/newsSlice';

const StockAnalysis: React.FC = () => {
  const dispatch = useDispatch();
  const articles = useSelector(selectArticles);
  const loading = useSelector(selectNewsLoading);
  const [selectedStock, setSelectedStock] = useState<string | null>(null);

  useEffect(() => {
    dispatch(fetchArticles());
  }, [dispatch]);

  // Extract unique stock symbols from articles
  const stockSymbols = Array.from(
    new Set(
      articles.flatMap((article) =>
        article.stock_mentions.map((mention) => mention.symbol)
      )
    )
  ).sort();

  // Filter articles for selected stock
  const stockArticles = selectedStock
    ? articles.filter((article) =>
        article.stock_mentions.some((mention) => mention.symbol === selectedStock)
      )
    : [];

  // Calculate sentiment data for the chart
  const sentimentData = stockArticles
    .sort((a, b) => new Date(a.published_at).getTime() - new Date(b.published_at).getTime())
    .map((article) => ({
      date: new Date(article.published_at).toLocaleDateString(),
      sentiment: article.sentiment_score || 0,
    }));

  // Calculate category distribution
  const categoryData = stockArticles.reduce((acc, article) => {
    article.categories.forEach((cat) => {
      acc[cat.category.name] = (acc[cat.category.name] || 0) + 1;
    });
    return acc;
  }, {} as Record<string, number>);

  const categoryChartData = Object.entries(categoryData).map(([name, count]) => ({
    name,
    count,
  }));

  // Calculate sentiment statistics
  const sentimentStats = {
    average: stockArticles.reduce((acc, article) => acc + (article.sentiment_score || 0), 0) / stockArticles.length || 0,
    positive: stockArticles.filter((article) => (article.sentiment_score || 0) > 0.2).length,
    negative: stockArticles.filter((article) => (article.sentiment_score || 0) < -0.2).length,
    neutral: stockArticles.filter((article) => Math.abs(article.sentiment_score || 0) <= 0.2).length,
  };

  if (loading) {
    return <LinearProgress />;
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Stock Analysis
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Autocomplete
            options={stockSymbols}
            value={selectedStock}
            onChange={(_, newValue) => setSelectedStock(newValue)}
            renderInput={(params) => (
              <TextField
                {...params}
                label="Select Stock Symbol"
                variant="outlined"
              />
            )}
            sx={{ mb: 3 }}
          />
        </Grid>

        {selectedStock && (
          <>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Sentiment Trend
                </Typography>
                <Box sx={{ height: 300 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={sentimentData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis domain={[-1, 1]} />
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

            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Category Distribution
                </Typography>
                <Box sx={{ height: 300 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={categoryChartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="count" fill="#1976d2" />
                    </BarChart>
                  </ResponsiveContainer>
                </Box>
              </Paper>
            </Grid>

            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Sentiment Statistics
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6} md={3}>
                      <Typography variant="subtitle2" color="text.secondary">
                        Average Sentiment
                      </Typography>
                      <Typography variant="h4">
                        {sentimentStats.average.toFixed(2)}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                      <Typography variant="subtitle2" color="text.secondary">
                        Positive Articles
                      </Typography>
                      <Typography variant="h4" color="success.main">
                        {sentimentStats.positive}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                      <Typography variant="subtitle2" color="text.secondary">
                        Negative Articles
                      </Typography>
                      <Typography variant="h4" color="error.main">
                        {sentimentStats.negative}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                      <Typography variant="subtitle2" color="text.secondary">
                        Neutral Articles
                      </Typography>
                      <Typography variant="h4" color="text.secondary">
                        {sentimentStats.neutral}
                      </Typography>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12}>
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Date</TableCell>
                      <TableCell>Title</TableCell>
                      <TableCell>Sentiment</TableCell>
                      <TableCell>Categories</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {stockArticles
                      .sort((a, b) => new Date(b.published_at).getTime() - new Date(a.published_at).getTime())
                      .map((article) => (
                        <TableRow key={article.id}>
                          <TableCell>
                            {new Date(article.published_at).toLocaleDateString()}
                          </TableCell>
                          <TableCell>{article.title}</TableCell>
                          <TableCell>
                            {(article.sentiment_score || 0).toFixed(2)}
                          </TableCell>
                          <TableCell>
                            {article.categories
                              .map((cat) => cat.category.name)
                              .join(', ')}
                          </TableCell>
                        </TableRow>
                      ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Grid>
          </>
        )}
      </Grid>
    </Box>
  );
};

export default StockAnalysis; 