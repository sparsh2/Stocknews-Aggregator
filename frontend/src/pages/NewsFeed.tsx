import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Box,
  Typography,
  Card,
  CardContent,
  CardActions,
  Grid,
  Chip,
  TextField,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  LinearProgress,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Link as LinkIcon,
  Category as CategoryIcon,
} from '@mui/icons-material';
import { RootState } from '../store';
import {
  fetchArticles,
  fetchCategories,
  selectArticles,
  selectCategories,
  selectNewsLoading,
} from '../store/slices/newsSlice';

const NewsFeed: React.FC = () => {
  const dispatch = useDispatch();
  const articles = useSelector(selectArticles);
  const categories = useSelector(selectCategories);
  const loading = useSelector(selectNewsLoading);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [sortBy, setSortBy] = useState<'date' | 'sentiment'>('date');

  useEffect(() => {
    dispatch(fetchArticles());
    dispatch(fetchCategories());
  }, [dispatch]);

  const filteredArticles = articles
    .filter((article) => {
      const matchesSearch = article.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        article.content.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesCategory = !selectedCategory ||
        article.categories.some(cat => cat.category.id === selectedCategory);
      return matchesSearch && matchesCategory;
    })
    .sort((a, b) => {
      if (sortBy === 'date') {
        return new Date(b.published_at).getTime() - new Date(a.published_at).getTime();
      }
      return (b.sentiment_score || 0) - (a.sentiment_score || 0);
    });

  const getSentimentColor = (score: number) => {
    if (score > 0.2) return 'success';
    if (score < -0.2) return 'error';
    return 'default';
  };

  const getSentimentIcon = (score: number) => {
    if (score > 0.2) return <TrendingUpIcon />;
    if (score < -0.2) return <TrendingDownIcon />;
    return null;
  };

  if (loading) {
    return <LinearProgress />;
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        News Feed
      </Typography>
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} md={4}>
          <TextField
            fullWidth
            label="Search articles"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </Grid>
        <Grid item xs={12} md={4}>
          <FormControl fullWidth>
            <InputLabel>Category</InputLabel>
            <Select
              value={selectedCategory}
              label="Category"
              onChange={(e) => setSelectedCategory(e.target.value)}
            >
              <MenuItem value="">All Categories</MenuItem>
              {categories.map((category) => (
                <MenuItem key={category.id} value={category.id}>
                  {category.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} md={4}>
          <FormControl fullWidth>
            <InputLabel>Sort By</InputLabel>
            <Select
              value={sortBy}
              label="Sort By"
              onChange={(e) => setSortBy(e.target.value as 'date' | 'sentiment')}
            >
              <MenuItem value="date">Date</MenuItem>
              <MenuItem value="sentiment">Sentiment</MenuItem>
            </Select>
          </FormControl>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {filteredArticles.map((article) => (
          <Grid item xs={12} key={article.id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                  <Typography variant="h6" component="div" sx={{ flex: 1 }}>
                    {article.title}
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', ml: 2 }}>
                    {article.sentiment_score !== null && (
                      <Tooltip title={`Sentiment: ${article.sentiment_score.toFixed(2)}`}>
                        <Chip
                          icon={getSentimentIcon(article.sentiment_score)}
                          label={article.sentiment_score.toFixed(2)}
                          color={getSentimentColor(article.sentiment_score)}
                          size="small"
                        />
                      </Tooltip>
                    )}
                  </Box>
                </Box>
                <Typography variant="body2" color="text.secondary" paragraph>
                  {article.summary}
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2 }}>
                  {article.categories.map((cat) => (
                    <Chip
                      key={cat.category.id}
                      icon={<CategoryIcon />}
                      label={cat.category.name}
                      size="small"
                    />
                  ))}
                </Box>
                <Typography variant="caption" color="text.secondary">
                  Published: {new Date(article.published_at).toLocaleString()}
                </Typography>
              </CardContent>
              <CardActions>
                <IconButton
                  size="small"
                  href={article.url}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <LinkIcon />
                </IconButton>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default NewsFeed; 