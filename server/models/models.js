const mongoose = require('mongoose');
const Schema = mongoose.Schema;

// URLs Collection Schema
const urlSchema = new Schema({
  url: { type: String, required: true, unique: true },
  created_at: { type: Date, default: Date.now }
});

// Keywords Collection Schema
const keywordSchema = new Schema({
  keyword: { type: String, required: true, unique: true },
  created_at: { type: Date, default: Date.now }
});

// Parsed Articles Collection Schema
const parsedArticleSchema = new Schema({
  title: { type: String, required: true },
  link: { type: String, required: true, unique: true },
  author: { type: String },
  published_date: { type: Date, required: true },
  url_id: { type: Schema.Types.ObjectId, ref: 'Url', required: true },
  created_at: { type: Date, default: Date.now }
});

// Scraped Content Collection Schema
const scrapedContentSchema = new Schema({
  parsed_article_id: { type: Schema.Types.ObjectId, ref: 'ParsedArticle', required: true },
  content: { type: String, required: true },
  created_at: { type: Date, default: Date.now }
});

// Filtered Articles Collection Schema
const filteredArticleSchema = new Schema({
  keyword_id: { type: Schema.Types.ObjectId, ref: 'Keyword', required: true },
  scraped_content_id: { type: Schema.Types.ObjectId, ref: 'ScrapedContent', required: true },
  created_at: { type: Date, default: Date.now }
});

// Summarized Content Collection Schema
const summarizedContentSchema = new Schema({
  scraped_content_id: { type: Schema.Types.ObjectId, ref: 'ScrapedContent', required: true },
  summary: { type: String, required: true },
  created_at: { type: Date, default: Date.now }
});

// User Data Collection Schema
const userSchema = new Schema({
  name: { type: String, required: true },
  username: { type: String, required: true, unique: true },
  password: { type: String, required: true },

  // User-specific URLs (subset of global URLs)
  urls: [{ 
    url_id: { type: Schema.Types.ObjectId, ref: 'Url' } 
  }],

  // User-specific Keywords (subset of global Keywords)
  keywords: [{ 
    keyword_id: { type: Schema.Types.ObjectId, ref: 'Keyword' } 
  }],

  // Feeds for the user's keywords
  feeds: [{
    keyword_id: { type: Schema.Types.ObjectId, ref: 'Keyword' },
    filtered_articles: [{
      filtered_article_id: { type: Schema.Types.ObjectId, ref: 'FilteredArticle' }
    }]
  }],

  // Summaries for the user's keywords
  summaries: [{
    keyword_id: { type: Schema.Types.ObjectId, ref: 'Keyword' },
    summaries: [{
      summary_id: { type: Schema.Types.ObjectId, ref: 'SummarizedContent' }
    }]
  }],

  created_at: { type: Date, default: Date.now }
});

// Compile Models from Schemas
const Url = mongoose.model('Url', urlSchema);
const Keyword = mongoose.model('Keyword', keywordSchema);
const ParsedArticle = mongoose.model('ParsedArticle', parsedArticleSchema);
const ScrapedContent = mongoose.model('ScrapedContent', scrapedContentSchema);
const FilteredArticle = mongoose.model('FilteredArticle', filteredArticleSchema);
const SummarizedContent = mongoose.model('SummarizedContent', summarizedContentSchema);
const User = mongoose.model('User', userSchema);

module.exports = {
  Url,
  Keyword,
  ParsedArticle,
  ScrapedContent,
  FilteredArticle,
  SummarizedContent,
  User
};
