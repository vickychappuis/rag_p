## Project Overview

### Ingestion

The first thing I did was start with ingestion. 

I looked around at the data I could get and decided to just ingest the website, because I didn't find any other trustworthy documentation about Promtior that wasn't their website.

LinkedIn could have been added, but although there are tools to scrape LinkedIn (like [PhantomBuster](https://phantombuster.com/))  you could get your account blocked (already happened to me one time). 

So I decided to just scrape the website (with [Firecrawl](https://www.firecrawl.dev/)) instead.

One of the challenges there was that the subdomain `careers.promtior.ai` didn't get picked up with a direct crawl. So I first used the **search** feature to discover all the different hosts, and then used the **crawl** feature on each host individually.

I also used the PDF from the technical assessment itself as a data source. I processed it with [Docling](https://www.docling.ai/). I know Docling is kind of heavy, and for processing a single PDF a lighter library would work fine. I chose Docling because over time implementing RAG, I've found it to be the only library you need to process many different file types — PDF, Excel, PowerPoint, Docx, etc. Once you get to know it deep, you don't have to spend time thinking about which library to use for extraction. Docling usually gets most things right, so that's why I wanted to use it here as the extraction tool. (It also has some nice chunkers)

### Chunking and Indexing

For chunking, I used [Chonkie](https://www.chonkie.ai/). It's an open source library that has many types of chunking and chunks really fast. I chose semantic chunking because I wanted to chunk in ways that felt semantically correct, this is a usual approach for simple Q&A systems.

For the embedding model, I didn't think about it much. I chose OpenAI. If it were a more niche project, I would go to the Hugging Face leaderboard and check out what's been ranking lately depending on the specific niche. But for this basic Q&A system, I just used good general models from OpenAI for both embedding and LLM response that I knew would be good.

### Vector Store

For the vector store, I chose Qdrant and hosted it on EC2. There are other options, in AWS you have OpenSearch Service, in Azure you have Azure AI Service, and AWS also has S3 Vectors. I decided on Qdrant because it's open source, and hosting Qdrant in AWS is way cheaper than OpenSearch.

### RAG Chain

For the agent part, I decided to just use an LLM. I didn't create an agent in LangChain, because we don't really need it for this particular assessment. It doesn't ask you for the agent to realize it has to use a vector search tool. So I just did the vector search automatically and passed the question along with the reference chunks to the LLM.

One thing I added later was a re-ranker, because the chunks I was getting at first were not really good. They could still be improved: for example, cleaning up the content from the extraction that has some image tags in it. But I decided not to, because in a normal project I would have a talk with the client asking about these images — if they want them, if they're useful, and whether this cleanup could have a negative effect. Sometimes that happens when you think about a RAG project in a certain scope and type of documents, and then later you have a broader and more diverse set of documents, and the restrictions you put at first that helped in a small scope end up working against you.

### Deployment

I used AWS as the cloud service and Terraform to define the infrastructure. I went with two EC2s — one for LangServe, another one for Qdrant — and an API Gateway in front.

For now, I decided to keep the ingestion part aside. If I had to continue with this project, one cool idea could be making an AWS Lambda to accept new files or URLs sent by the user. So if a user wants to seed the database, they could make a POST to an endpoint in the API Gateway with a URL or a file, and the API Gateway would trigger a Lambda function that would extract, chunk, and index. The only limitation there would be that we would probably need a lighter dependency for extraction — as I said, Docling is pretty heavy, but we could consider other options if we wanted that feature.

### Future To-Dos

- **Evaluations**: If we had a broad preset Q&A database, we could evaluate this RAG. I wrote a blog about it: https://vickychappuis.dev/blogs/evaluating-rag-systems
- **Cache**: For frequently asked questions, we could add cache. I also talk about this in a blog: https://vickychappuis.dev/blogs/ai-and-cache ("The easiest win")
- **Conversation history**: Setting up the agent to have conversation history. There are many ways to do that — with a relational database, with a cache, or using LangChain's built-in features for that.
- **Better references in the prompt**: Edit the prompt so that the answer refers you to the referenced links it got from the retrieved chunks.
- **Better UI**: Show retrieved chunks in the interface, or even have an S3 service where we save files (like the PDF from the assessment) and make them easily accessible to the user when we refer to them in an answer.
- **Authentication**: For now I just have a spend limit on the OpenAI API, but we should add proper auth to manage access.
