Problems I ran into:

- I had issues with venvs, specifically with managing library dependencies for projects, that was before I learned Docker could be used to render venvs obsolete.

- Was not using any form of logging at all, so it was hard for me to test my projects as I wouldn't know what succeeded or failed. Again at this time I was not using Docker, so my first solution was to write literal logs to local phyiscal directories, such as "all tests passed", or simple checkpoint messages. I eventually realizied that this had two drawbacks, firstly it was not easy to efficiently sort through logs to find what errors were present, and it would eventually require more physical disk space. MY solution ended up being to use Docker logs as a cloud based solution for logging, as well as making my logs json formatted for better compatibility with modern logging methods other than docker, such as popular ELK and EFK stacks.

- I had been for a long time using main.py instead of apache airflow as my orchestration method for my ETL pipeline was initially how I intended to go forward, but after learning of the ubiquity and demand of Apache Airflow, I decided on refactoring my project to switch to meet industry standards for orchestration. I did this to avoid using cron jobs in a production setting due to reliability concerns, which main.py would have undoubtedly required.

- Was using test/ directory incorrectly, as I had an exact copy of my entire working directory just for testing. I had learned that this approach was inefficient and that tests should focus on unit tests, integration tests and end-to-end tests, that call my pipeline with sample or mocked data

- Accessing docker logs..?
- Data governance on Cloud providers AWS/Azure

- I had always thought that 'testing' stopped at just executing the program via docker containers, and if everything went as planned, and logs that were descriptive told you what you wanted, then tests were complete. The reality however, was that testing is more than just if your project "works", it comes down to verifying the durability of core functions, methods, utility logic, modules working together, bug prevention, scalability and performance. I had not done anything of the nature up until now, so I was prompted to remove the copy of my project in the test directory, and replace it with a variety of tests.
