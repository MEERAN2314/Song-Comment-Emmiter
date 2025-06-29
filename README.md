# Song-Comment-Emmiter

This project analyzes YouTube comments to gauge public sentiment.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

* Python 3.7 or higher
* pip (Python package installer)

### Installing

1. **Clone the repository:**

   ```bash
   git clone [repository_url]
   cd Song-Comment-Emmiter
   ```

2. **Create a .env file:**  Create a file named `.env` in the root directory of the project.  This file will store your API keys and other sensitive information.  You'll need to obtain your own YouTube Data API v3 key.  An example `.env` file is shown below:

   ```
   YOUTUBE_API_KEY=YOUR_YOUTUBE_API_KEY
   ```

3. **Set up MongoDB URI:** Add your MongoDB connection string to the `.env` file.  This string should be obtained from your MongoDB Atlas cluster.  It will look something like this:

   ```
   MONGO_URI=mongodb+srv://<username>:<password>@<cluster-address>/<database-name>?retryWrites=true&w=majority
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

### Running

1. **Run the application:**

   ```bash
   python app.py
   ```

## Running Tests

To run the tests, execute the following command:

```bash
python -m unittest test_connectionDB.py
```

## Built With

* Python - Programming Language
* pymongo - MongoDB Driver
* YouTube Data API v3 - Data Source
* Streamlit
* MCP(Model Context Protocol)

## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b feature/AmazingFeature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin feature/AmazingFeature`
5. Submit a pull request :D

## Authors

* **J MEERAN ASHFAAQ** - *YOUTUBR SONG COMMENT EMMITER* - MEERAN2314

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
