# Who_Detects_Better
A repository containing the dataset and code for our paper.

In our questioning of large models, only ChatGPT-4o did not utilize an API interface but instead employed simulated keyboard input, while the rest used the API interface for batch querying. Among these, generator_prompt.py is responsible for simulating keyboard input, while output_convert.py stores the model's response data in a tabular format. The other files, named after the respective models, are those that use the model's API interface for querying. ErrorMessagesDataset is the error information dataset we constructed, which includes randomly selected erroneous information from the questionnaire creation process.
