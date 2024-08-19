const express = require('express');
const { PythonShell } = require('python-shell');

const app = express();
app.use(express.json());

app.post('/parse-rss', (req, res) => {
  const { rss_urls } = req.body;

  if (!rss_urls || !Array.isArray(rss_urls)) {
    return res.status(400).json({ error: 'rss_urls should be an array of URLs' });
  }

  const options = {
    mode: 'text',
    pythonOptions: ['-u'], // get print results in real-time
    args: [JSON.stringify(rss_urls)]
  };

  PythonShell.run('path_to_your_script/xml_parser_tool.py', options, function (err, results) {
    if (err) {
      console.error(err);
      return res.status(500).json({ error: 'Failed to parse RSS feeds' });
    }
    else{
        console.log("success")
    }

app.post('/scrape-content', (req, res) => {
  // Assuming that the state is managed within your LangGraph setup
  const options = {
    mode: 'text',
    pythonOptions: ['-u'], // get print results in real-time
    args: []  // No need to pass args as everything is managed by the LangGraph workflow
  };

  PythonShell.run('path_to_your_script/content_scraper_tool.py', options, function (err, results) {
    if (err) {
      console.error(err);
      return res.status(500).json({ error: 'Failed to scrape content' });
    } else {
      console.log("Success");
    }

    // Assuming the Python script returns a JSON string of the scraped articles
    const scrapedArticles = JSON.parse(results[0]);
    res.status(200).json({ scrapedArticles });
  });
});    

    // Assuming the Python script returns a JSON string of the parsed articles
    const parsedArticles = JSON.parse(results[0]);
    res.status(200).json({ parsedArticles });
  });
});

app.post('/filter-keywords', (req, res) => {
    // Assuming that the state is managed within your LangGraph setup
    const options = {
      mode: 'text',
      pythonOptions: ['-u'], // get print results in real-time
      args: []  // No need to pass args as everything is managed by the LangGraph workflow
    };
  
    PythonShell.run('path_to_your_script/keyword_filter_tool.py', options, function (err, results) {
      if (err) {
        console.error(err);
        return res.status(500).json({ error: 'Failed to filter keywords' });
      } else {
        console.log("Success");
      }
  
      // Assuming the Python script returns a JSON string of the filtered articles
      const filteredArticles = JSON.parse(results[0]);
      res.status(200).json({ filteredArticles });
    });
  });

  app.post('/summarize', (req, res) => {
    const options = {
      mode: 'text',
      pythonOptions: ['-u'], // get print results in real-time
      args: []  // No need to pass args as everything is managed by the LangGraph workflow
    };
  
    PythonShell.run('path_to_your_script/summarization_agent.py', options, function (err, results) {
      if (err) {
        console.error(err);
        return res.status(500).json({ error: 'Failed to summarize articles' });
      } else {
        console.log("Success");
      }
  
      // Assuming the Python script returns a JSON string of the summaries
      const summaries = JSON.parse(results[0]);
      res.status(200).json({ summaries });
    });
  });  

// Start the server
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
