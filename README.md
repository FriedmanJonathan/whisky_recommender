# Whisky Recommender Project

## Overview

The Whisky Recommender Project aims to help users discover new whiskies based on their preferences. The project involves web scraping whisky data, processing it, and using machine learning to recommend whiskies that match user tastes. Users can select their favorite whiskies and get recommendations along with common and additional tasting notes.

## Project Structure

The basic structure of the project is as follows:

```plaintext
whisky_recommender/
├── backend/
│   ├── app.py
├── data/
│   ├── feedback/
│   │   └── 2024_05/
│   │       └── feedback_file_dated1.csv
│   │       └── feedback_file_dated2.csv
│   ├── processed/
│   │   └── 2024_05/
│   │       └── whisky_features.csv
│   └── raw/
│       └── 2024_05/
│           ├── whisky_main_page_with_ratings.csv
│           └── whisky_details_all.csv
├── frontend/
│   ├── index.html
│   ├── script.js
│   ├── style.css
│   └── distillery_data.csv
├── scripts/
│   ├── processing/
│   │   └── data_parsing_and_cleaning.csv
│   ├── modeling/
│   │   └── whisky_recommender_model.py
│   ├── ingestion/
│   │   └── whisky_com_main_page_scraper.csv
│   │   └── whisky_com_secondary_pages_scraper.csv
├── tests/
│   └── test_data_parsing.py
├── gitignore
├── LICENSE
├── Makefile
├── requirements.txt
└── README.md

```

## Installation

1. Clone the repository:

git clone https://github.com/yourusername/whisky_recommender.git
cd whisky_recommender

2. Set up a virtual environment:

python -m venv .whisky_rec_venv

3. Activate the virtual environment:

Windows: .whisky_rec_venv\Scripts\activate
MacOS/Linux: source .whisky_rec_venv/bin/activate

4. Install the required packages:

make install

5. Run the project

Run python app.py in the backend folder and then access on your browser at http://localhost:8000


6. Running Tests

To run tests, use the following command: make test

7. Linting and Formatting

To lint the code using pylint and format it using black, run the commands make lint of make format, respectively.

## Project Components

### Web Scraping

The synchronous scraping module uses Selenium and BeautifulSoup to scrape whisky data from the Whisky.com website.

### Data Parsing

The data_parsing_and_modeling.py script processes the outputs of the whisky scraping scripts into a feature dataset. It prepares the data required for generating whisky recommendations.

### Whisky Recommender Model

The whisky_recommender_model.py script generates recommendations based on user-selected whiskies. It uses cosine similarity to compare user-selected whisky profiles with other whiskies in the dataset.


## Next steps: Deploying to Production


When running locally via Docker, make sure:

1. Your .env file has the correct settings: IS_LOCAL = True.
2. Command is docker build whisky-recommender 

3. eb setenv IS_LOCAL=False S3_BUCKET=whisky-recommender

The ultimate goal is to create a web interface where users can select their favorite whiskies and receive recommendations. The frontend consists of HTML, JavaScript, and CSS files, while the backend is built with Python.

eb create whisky-recommender --single --instance_type t3.micro
We use single to not introduce a load balancer not multiple EC2 instances as this is a small app for now. 

To delete, we can make use of the delete_vpc_and_dependencies_on_aws.py script. This is 




## Deployment on AWS

This version of the Whisky Recommender is a web application designed to recommend whiskies based on user preferences. The application is built using Flask and can be deployed on AWS Elastic Beanstalk. Users can submit feedback, which is stored in an S3 bucket.

### Prerequisites
- AWS account
- AWS CLI installed and configured
- Appropriate IAM user with permissions to deploy applications and interact with S3

### Steps to Deploy

1. **Set Up Environment Variables**:
   - Create a `.env` file in the root directory of your project.
   - Add the following environment variables:
     ```plaintext
     IS_LOCAL=False
     S3_BUCKET=your-s3-bucket-name
     ```

2. **Create an S3 Bucket**:
   - Create an S3 bucket in the same region as your Elastic Beanstalk environment.
   - Ensure your IAM user has permissions to `s3:PutObject`, `s3:GetObject`, and `s3:ListBucket` for this bucket.

3. **Give Appropriate Permissions**:
   - Ensure the IAM role associated with your Elastic Beanstalk environment has the necessary permissions to access the S3 bucket.
   - Update your bucket policy to allow access from the Elastic Beanstalk instance profile role:
     ```json
     {
         "Version": "2012-10-17",
         "Statement": [
             {
                 "Effect": "Allow",
                 "Principal": {
                     "AWS": "arn:aws:iam::<account-id>:role/<instance-profile-role-name>"
                 },
                 "Action": [
                     "s3:PutObject",
                     "s3:GetObject",
                     "s3:ListBucket"
                 ],
                 "Resource": [
                     "arn:aws:s3:::your-s3-bucket-name",
                     "arn:aws:s3:::your-s3-bucket-name/*"
                 ]
             }
         ]
     }
     ```

4. **Deploy to AWS Elastic Beanstalk**:
   - Use the following commands to deploy:
     ```bash
     eb init # here you'll interactively configure region, Docker setup, etc. 
     eb create my-whisky-recommender-env --instance_type t3.micro --single
     eb deploy
     ```

5. **Set Up Region Compatibility**:
   - Ensure that the S3 bucket and Elastic Beanstalk environment are in the same AWS region to avoid region compatibility issues.

6. **Remove the Project**:
   - To remove the project, use the script provided:
     ```bash
     python delete_vpc_and_dependencies_on_aws.py
     ```

### Environment Variables
- `IS_LOCAL`: Set to `True` for local development and `False` for deployment on AWS.
- `S3_BUCKET`: The name of the S3 bucket to store feedback.

## Future Plans
### Route 53 Integration
- **Set Up a Domain**: Plan to use Route 53 to set up a custom domain for the application, improving accessibility and professional appearance.

### AWS Step Functions and Lambda
- **Automate Monthly Updates**: Implement AWS Step Functions and Lambda to automate the monthly scraping and updating of whisky data from the website.

### Current Limitations
- **Website Loading Issues**: The whisky website currently has loading issues that prevent the scraping script from accessing all content. The script cannot scroll past the first page, limiting the data that can be scraped and processed.

## Conclusion
This project demonstrates a full-stack web application deployment using AWS services. Future enhancements aim to automate data updates and improve user experience with custom domain integration.



## Feedback and Contributions

Feedback and contributions are welcome! Please fork the repository and create a pull request with your changes. For major changes, please open an issue first to discuss what you would like to change.


## License

This project is licensed under the MIT License. See the LICENSE file for details.