const express = require('express');
const mongoose = require('mongoose');
const app = express()
// Import and load environment variables
const dotenv = require('dotenv');
dotenv.config();

// Access environment variables
const mongoURI = process.env.MONGODB_URI;
const port = process.env.PORT;

app.get('/', (req, res) => {
    res.send('Hello World!')
})

mongoose.connect(mongoURI, { useNewUrlParser: true, useUnifiedTopology: true });

// Listen for the database connection event
mongoose.connection.on('connected', () => {
    console.log('Connected to MongoDB');
    
    // List all collections (models) in the database
    const collections = mongoose.connection.collections;
    console.log(collections)
    const collectionNames = Object.keys(collections);
    
    console.log('Collections in the database:');
    collectionNames.forEach((collectionName) => {
        console.log(collectionName);
    });
});
  
// Handle database connection errors
mongoose.connection.on('error', (err) => {
    console.error('MongoDB connection error:', err);
});

app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});