# !pip install bs4
# !pip install selenium
# !pip install lxml
# !pip install chardet
# !pip install transformers
# !pip3 install torch torchvision torchaudio
# !pip install ipywidgets
# !pip install tensorflow
# !pip install py_vncorenlp
# !pip install pyvi

import requests
from bs4 import BeautifulSoup
import re
from dataclasses import dataclass
import datetime

@dataclass
class Articles:
    url: str
    lastmod: str
    title: str
    caption: str
    categories: str
    abstract: str
    text: str
    abstract_sentiment: str
    last_processed: str
    
    not_available = 'n/a'
    
    def __init__(self, url = not_available, lastmod = not_available, title = not_available, caption = not_available, categories = not_available, abstract = not_available, text = not_available, abstract_sentiment = not_available, last_processed = not_available):
        self.url = url
        self.lastmod = lastmod
        self.title = title
        self.caption = caption
        self.categories = categories
        self.abstract = abstract
        self.text = text
        self.abstract_sentiment = abstract_sentiment
        self.last_processed = last_processed


    @classmethod
    def vietify(cls, cdata):
        try:
            viet = cdata.encode('latin-1').decode('utf-8')
        except Exception as e:
            viet = cdata
        viet = viet.replace('<![CDATA[','').replace(']]>','')
        return viet
    @classmethod
    def linify_text(cls, text):
        to_be_replaceds = ['\n', 
                            '\u2028',
                            '\u2029',
                            '<br/>',
                            '\\xa0',
                            '\\u200f',
                            '\\u200b',
                            '\\ufeff',
                            '\xa0',
                            '\t']
        for word in to_be_replaceds:
            text = text.replace(word,' ')
        slash_pattern = r"\\+"
        text = re.sub(slash_pattern, "", text)
        text = text.strip()
        return text
    
    @classmethod
    def from_dict(cls, article_dict):
        return cls(**article_dict)
    @classmethod
    def from_line(cls, line):
        # Extract attribute-value pairs
        pattern = r"(\w+)\s*=\s*'(.*?)'"
        matches = re.findall(pattern, line)
        
        # Create a dictionary to store the attribute-value pairs
        article_dict = {}
        for attr, value in matches:
            article_dict[attr] = value

        return cls(**article_dict)

    requests_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36'
        }
    
    def process_url(self):
        html_text = requests.get(self.url, headers = Articles.requests_headers).text
        soup = BeautifulSoup(html_text, 'lxml')
        title = Articles.linify_text(soup.find('h1', class_ = 'title').text) # type: ignore
        published_time = Articles.linify_text(soup.find('span', class_ = 'pdate').text) # type: ignore
        categories_list = soup.find_all('a', class_ = 'category-page__name cat')
        categories = ''
        for category in categories_list:
            categories = categories + Articles.linify_text(category.text) + ', '
        categories = categories[:-2]
        abstract = Articles.linify_text(soup.find('h2', class_ = 'sapo').text) # type: ignore
        text_container = soup.find('div', class_ = 'detail-content afcbc-body')
        texts = text_container.find_all('p') # type: ignore
        text = ''
        for content in texts:
            text = text + Articles.linify_text(content.text)
        self.title = title
        self.categories = categories
        self.abstract = abstract
        self.text = text
        if self.lastmod == Articles.not_available:
            self.lastmod = published_time
        
    def write(self, file_path, mode = 'a', encoding = 'utf-8'):
        with open(file_path, mode = mode, encoding = encoding) as file:
            file.write(str(self))
            file.write('\n')

class ArticleManagers:
    def __init__(self, excluded_articles_file_path = ''):
        self.excluded_articles = self.get_articles(excluded_articles_file_path)
        self.excluded_articles_file_path = excluded_articles_file_path
                
    def get_articles(self, file_path):
        articles = []
        try:
            with open(file_path, "r", encoding= 'utf-8') as file:
                for line in file:
                    try:
                        line = Articles.linify_text(line)
                        article = Articles.from_line(line)
                        if 'http' in article.url:
                            articles.append(article)
                    except Exception as e:
                        print(f'ERROR getting articles: {type(e).__name__} from {file_path}')
            print(f'Finished file {file_path}, got {len(articles)} articles.')
        except FileNotFoundError:
            print(f'Articles file not found at: {file_path}')
        return articles
    
    def save_articles(self, articles, file_path, mode = 'w', encoding = 'utf-8'):
        with open(file = file_path, mode = mode, encoding = encoding) as file:
            for article in articles:
                file.write(str(article))
                file.write("\n")
                
    def remove_duplicate_urls(self, file_path):
        unique_urls = set()
        articles = self.get_articles(file_path=file_path)
        for article in articles:
            pre_adding_length = len(unique_urls)
            unique_urls.add(article.url)
            post_adding_length = len(unique_urls)
            if pre_adding_length == post_adding_length:
                articles.remove(article)
        self.save_articles(articles= articles, file_path= file_path, mode = 'w')

    @classmethod
    def crawl_submaps_from_sitemap(cls, sitemap_url):
        submaps = []
        if 'cafef' in sitemap_url:
            html_text = requests.get(sitemap_url, headers = Articles.requests_headers).text
            soup = BeautifulSoup(html_text, 'lxml')
            containers = soup.find_all('sitemap') 
            for container in containers:
                submap_url = container.find('loc').text
                if r'https://cafef.vn/sitemaps/sitemaps-' in submap_url:                
                    lastmod = container.find('lastmod').text
                    submap_dict = {'url': submap_url, 'lastmod': lastmod}
                    submap = Articles.from_dict(submap_dict)
                    submaps.append(submap)    
        return submaps
    
    @classmethod
    def crawl_articles_from_submap(cls, submap):
        crawled_articles = []
        submap_url = submap.url
        sitemap_html_text = requests.get(submap_url).text
        sitemap_soup = BeautifulSoup(sitemap_html_text, 'lxml')
        url_containers = sitemap_soup.find_all('url') 
        for container in url_containers:
            url = Articles.linify_text(container.find('loc').text)
            if 'http' in url:
                time = Articles.linify_text(container.find('lastmod').text)
                title_cdata = Articles.linify_text(container.find('image:title').text)
                title_viet = Articles.vietify(title_cdata)
                caption_cdata = Articles.linify_text(container.find('image:caption').text)
                caption_viet = Articles.vietify(caption_cdata)
                article_dict = {'url': url, 'lastmod': time, 'title': title_viet, 'caption': caption_viet}
                article = Articles.from_dict(article_dict)
                crawled_articles.append(article)
        print(f'Processed: {submap_url}: got {len(crawled_articles)} articles.')
        return crawled_articles
    
    
    @classmethod
    def get_paths_from_submap(cls, submap, output_folder_path):
        _, crawled_name, processed_name = ArticleManagers.get_file_name_from_submap(submap)
        crawled_articles_file_path = output_folder_path + crawled_name
        processed_articles_file_path = output_folder_path + processed_name
        return crawled_articles_file_path, processed_articles_file_path
    
    @classmethod
    def get_file_name_from_submap(cls, submap):
        extracted_name = submap.url[submap.url.rfind("/") + 1:submap.url.rfind(".xml")]
        crawled_name = extracted_name + '.txt'
        processed_name = extracted_name + '_processed.txt'
        return extracted_name, crawled_name, processed_name

    
    def crawl_and_save_sitemap(self, sitemap_url, processed_submaps_file_path, output_folder_path):
        self.processed_submaps = self.get_articles(processed_submaps_file_path)
        # processed_submaps_urls = {processed_submap.url for processed_submap in self.processed_submaps}

        submaps = ArticleManagers.crawl_submaps_from_sitemap(sitemap_url)
        for submap in submaps:
            # if submap.url in processed_submaps_urls:
            check = 'unprocessed'
            for index, processed_submap in enumerate(self.processed_submaps):
                if (processed_submap.url == submap.url):
                    if (processed_submap.lastmod == submap.lastmod):
                        check = 'already_processed'
                    else:
                        check = 'out_of_date'
                        duplicate_submap_index = index
                            
            if check == 'already_processed':
                continue

            articles = ArticleManagers.crawl_articles_from_submap(submap)

            if articles:
                if check == 'unprocessed':
                    self.processed_submaps.append(submap)
                if check == 'out_of_date':
                    self.processed_submaps[duplicate_submap_index] = submap
                crawled_articles_file_path = ArticleManagers.get_paths_from_submap(submap, output_folder_path)[0]
                self.save_articles(articles, crawled_articles_file_path, mode = 'w')
                self.save_articles(self.processed_submaps, processed_submaps_file_path, mode = 'w')

    def process_articles(self, articles_to_process):
        processed_articles = []
        for article in articles_to_process:
            try:
                article.process_url()
                processed_articles.append(article)
            except Exception as e:
                self.excluded_articles.append(article)
                print(f'ERROR processing article: {type(e).__name__}: {article.url}. Added to excluded articles')
        return processed_articles
    
    def process_and_save(self, crawled_articles_file_path,  processed_articles_file_path, total = 0, step = 10):
        self.crawled_articles = self.get_articles(crawled_articles_file_path)
        self.processed_articles = self.get_articles(processed_articles_file_path)
        processed_urls = {article.url for article in self.processed_articles}
        excluded_urls = {article.url for article in self.excluded_articles}
        unprocessed_articles = []
        if total == 0:
            total = len(self.crawled_articles)
        for article in self.crawled_articles:
            if (article.url not in processed_urls) and (article.url not in excluded_urls) and (article.url.strip()):
                unprocessed_articles.append(article)
            if len(unprocessed_articles) == total:
                break
        
        finished = len(self.processed_articles)
        loops = int(total // step + min(total % step, 1)) # if there is any remainder after loops, do an extra loop
        for i in range(0, loops):
            if i == loops - 1 and total % step:
                step = total % step
            step = min(step, len(unprocessed_articles))

            processing_articles = unprocessed_articles[:step]
            del unprocessed_articles[:step]
            processed_articles = self.process_articles(processing_articles)
            
            if processed_articles:
                try:
                        self.save_articles(articles = processed_articles, file_path = processed_articles_file_path, mode = 'a')
                        self.processed_articles = self.processed_articles + processed_articles
                except Exception as e:
                    print(f'ERROR updating processed articles file: {type(e).__name__}.')

            try:
                self.save_articles(articles = self.excluded_articles, file_path = self.excluded_articles_file_path, mode = 'w')
            except Exception as e:
                print(f'ERROR updating excluded articles file: {type(e).__name__}.')
                
            finished = finished + step
            if finished % 100 == 0:
                print(f'Processed {finished}/{total} articles. {len(self.crawled_articles) - finished} unprocessed urls remaining')          
            if len(unprocessed_articles) == 0:
                print('Finished. No more unprocessed articles.')
                break

    def sentiment_analysis(self, articles):
        from pyvi import ViTokenizer
        import torch
        from transformers import AutoModel, AutoTokenizer
        from numpy import average
        
        model_name = "vinai/phobert-base-v2"  # Vietnamese BERT model
        phobert = AutoModel.from_pretrained(model_name)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        for index, article in enumerate(articles):
            if article.abstract_sentiment == Articles.not_available:
                segmented = ViTokenizer.tokenize(article.abstract)
                input_ids = torch.tensor([tokenizer.encode(segmented)])
                try:
                    with torch.no_grad():
                        features = phobert(input_ids)  # Models outputs are now tuples    
                    article.abstract_sentiment = str(average(features[1]))
                except Exception as e:
                    print(f'Error analyzing sentiment of {article.url}: {type(e).__name__}. Abstract: {article.abstract}')
            if (index + 1) % 100 == 0:
                print(f'Analyzed sentiment of {index + 1}/{len(articles)} articles.')

    @classmethod
    def get_iso_from_current_time(cls):
        current_time = datetime.datetime.now()
        offset = datetime.datetime.now().astimezone().strftime("%z")
        colon_offset = offset[:-2] + ":" + offset[-2:]
        iso_time = current_time.strftime("%Y-%m-%dT%H:%M:%S") + colon_offset
        return iso_time

    def process_urls_from_submaps(self, processed_submaps_file_path, output_folder_path):
        self.processed_submaps = self.get_articles(processed_submaps_file_path)
        lastmods = []
        for submap in self.processed_submaps:
            lastmod = datetime.datetime.fromisoformat(submap.lastmod)
            lastmods.append(lastmod)
        self.processed_submaps = sorted(self.processed_submaps, key = lambda x: lastmods[self.processed_submaps.index(x)], reverse = True)
        for submap in self.processed_submaps:
            lastmod = datetime.datetime.fromisoformat(submap.lastmod)
            try:
                last_processed = datetime.datetime.fromisoformat(submap.last_processed)
            except Exception as e:
                last_processed = submap.last_processed
            if (last_processed == Articles.not_available) or (lastmod > last_processed):
                crawled_articles_file_path, processed_articles_file_path = ArticleManagers.get_paths_from_submap(submap, output_folder_path)
                self.process_and_save(crawled_articles_file_path, processed_articles_file_path)
                submap.last_processed = ArticleManagers.get_iso_from_current_time()
                self.save_articles(self.processed_submaps, processed_submaps_file_path, 'w')
                print(f'Finished processing {submap.url}.')
            
