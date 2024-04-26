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
    """Là class thể hiện các bài báo (news), nhằm quản lý dữ liệu
    """    
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
        """Tạo object articles. với các thông số đường dẫn, ngày đăng, tiêu đề, caption (ảnh đại diện), 
        chủ đề, câu tóm tắt (trong bài báo), nội dung bài báo, đánh giá cảm xúc, và thời gian xử lý

        Args:
            url (str, optional): Đường dẫn. Defaults to not_available.
            lastmod (str, optional): Ngày đăng. Defaults to not_available.
            title (str, optional): Tiêu đề. Defaults to not_available.
            caption (str, optional): Caption ảnh đại diện. Defaults to not_available.
            categories (str, optional): Chủ đề. Defaults to not_available.
            abstract (str, optional): Câu tóm tắt (là câu có sẵn, khác với phần NER + tóm tắt ở model GPT). Defaults to not_available.
            text (str, optional): Nội dung bài báo. Defaults to not_available.
            abstract_sentiment (str, optional): Đánh giá cảm xúc câu tóm tắt (không dùng nữa). Defaults to not_available.
            last_processed (str, optional): Ngày xử lý. Defaults to not_available.
        """        
        self.url = url
        self.lastmod = lastmod
        self.title = title
        self.caption = caption
        self.categories = categories
        self.abstract = abstract
        self.text = text
        self.abstract_sentiment = abstract_sentiment
        self.last_processed = last_processed

    def process_url(self):
        """Crawl các trường dữ liệu từ đường dẫn
        """        
        html_text = requests.get(self.url, headers = Articles.requests_headers).text
        soup = BeautifulSoup(html_text, 'lxml')
        title = Articles._linify_text(soup.find('h1', class_ = 'title').text) # type: ignore
        published_time = Articles._linify_text(soup.find('span', class_ = 'pdate').text) # type: ignore
        categories_list = soup.find_all('a', class_ = 'category-page__name cat')
        categories = ''
        for category in categories_list:
            categories = categories + Articles._linify_text(category.text) + ', '
        categories = categories[:-2]
        abstract = Articles._linify_text(soup.find('h2', class_ = 'sapo').text) # type: ignore
        text_container = soup.find('div', class_ = 'detail-content afcbc-body')
        texts = text_container.find_all('p') # type: ignore
        text = ''
        for content in texts:
            text = text + Articles._linify_text(content.text)
        self.title = title
        self.categories = categories
        self.abstract = abstract
        self.text = text
        if self.lastmod == Articles.not_available:
            self.lastmod = published_time
        
    def write(self, file_path, mode = 'a', encoding = 'utf-8'):
        """Ghi articles theo định dạng của `dataclass`

        Args:
            file_path (str): Đường dẫn tới file .txt
            mode (str, optional): Chế độ mở file. Defaults to 'a'.
            encoding (str, optional): Loại encoding. Defaults to 'utf-8'.
        """        
        with open(file_path, mode = mode, encoding = encoding) as file:
            file.write(str(self))
            file.write('\n')


    @classmethod
    def _vietify(cls, cdata):
        """Chuyển đổi những trường hợp bị encode sai thành unicode tiếng Việt (utf-8)

        Args:
            cdata (str): nội dung đầu vào

        Returns:
            str: Nội dung đã Việt hóa
        """        
        try:
            viet = cdata.encode('latin-1').decode('utf-8')
        except Exception:
            viet = cdata
        viet = viet.replace('<![CDATA[','').replace(']]>','')
        return viet
    
    @classmethod
    def _linify_text(cls, text):
        """Loại bỏ các ký tự đặc biệt trong nội dung báo

        Args:
            text (str): Nội dung input

        Returns:
            str: Nội dung đã loại bỏ các ký tự đặc biệt
        """        
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
    def _from_dict(cls, article_dict):
        """Tạo article từ dictionary

        Args:
            article_dict (dict): Dictionary lưu trữ thông tin về article

        Returns:
            article: object article
        """        
        return cls(**article_dict)
    
    @classmethod
    def _from_line(cls, line):
        """Tạo article từ 1 line trong file text (theo định dạng của `dataclass`)

        Args:
            line (str): Line trong file .txt

        Returns:
            article: Object article
        """        
        # Extract attribute-value pairs
        pattern = r"(\w+)\s*=\s*'(.*?)'"
        matches = re.findall(pattern, line)
        
        # Create a dictionary to store the attribute-value pairs
        article_dict = {}
        for attr, value in matches:
            article_dict[attr] = value

        return cls(**article_dict)

    # Giả mạo browser bình thường, tránh bị chặn
    requests_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36'
        }
    
class ArticleManagers:
    """Class để quản lý các lists gồm các articles
    """    

    def __init__(self, excluded_articles_file_path = ''):
        """Tạo object article_managers

        Args:
            excluded_articles_file_path (str, optional): Đường dẫn tới file .txt ghi các articles không xử lý được (để tránh xử lý lại nhiều lần). Defaults to ''.
        """        
        self.excluded_articles = self.get_articles(excluded_articles_file_path)
        self.excluded_articles_file_path = excluded_articles_file_path

    def crawl_and_save_sitemap(self, sitemap_url, processed_submaps_file_path, output_folder_path):
        """Function chính:
        (1) Tìm toàn bộ submap từ sitemap,
        (2) Tìm toán bộ đường dẫn articles trong các sitemaps, và
        (3) Crawl hoàn chính các articles và lưu trữ trong file .txt

        Args:
            sitemap_url (_type_): _description_
            processed_submaps_file_path (_type_): _description_
            output_folder_path (_type_): _description_
        """        
        self.processed_submaps = self.get_articles(processed_submaps_file_path)
        # processed_submaps_urls = {processed_submap.url for processed_submap in self.processed_submaps}

        submaps = ArticleManagers._crawl_submaps_from_sitemap(sitemap_url)
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

            articles = ArticleManagers._crawl_articles_from_submap(submap)

            if articles:
                if check == 'unprocessed':
                    self.processed_submaps.append(submap)
                if check == 'out_of_date':
                    self.processed_submaps[duplicate_submap_index] = submap
                crawled_articles_file_path = ArticleManagers._get_paths_from_submap(submap, output_folder_path)[0]
                self.save_articles(articles, crawled_articles_file_path, mode = 'w')
                self.save_articles(self.processed_submaps, processed_submaps_file_path, mode = 'w')

    @classmethod
    def _crawl_submaps_from_sitemap(cls, sitemap_url):
        """Crawl các submaps từ sitemap

        Args:
            sitemap_url (str): Đường dẫn của sitemap

        Returns:
            list: List các submaps (chia theo thời gian) tìm được
        """        
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
                    submap = Articles._from_dict(submap_dict)
                    submaps.append(submap)    
        return submaps
    
    @classmethod
    def _crawl_articles_from_submap(cls, submap):
        """Crawl các articles trong từng submap

        Args:
            submap (article): Object article submap

        Returns:
            list: List các articles đã crawl được
        """        
        crawled_articles = []
        submap_url = submap.url
        sitemap_html_text = requests.get(submap_url).text
        sitemap_soup = BeautifulSoup(sitemap_html_text, 'lxml')
        url_containers = sitemap_soup.find_all('url') 
        for container in url_containers:
            url = Articles._linify_text(container.find('loc').text)
            if 'http' in url:
                time = Articles._linify_text(container.find('lastmod').text)
                title_cdata = Articles._linify_text(container.find('image:title').text)
                title_viet = Articles._vietify(title_cdata)
                caption_cdata = Articles._linify_text(container.find('image:caption').text)
                caption_viet = Articles._vietify(caption_cdata)
                article_dict = {'url': url, 'lastmod': time, 'title': title_viet, 'caption': caption_viet}
                article = Articles._from_dict(article_dict)
                crawled_articles.append(article)
        print(f'Processed: {submap_url}: got {len(crawled_articles)} articles.')
        return crawled_articles

    def process_and_save(self, crawled_articles_file_path,  processed_articles_file_path, total = 0, step = 10):
        """_summary_

        Args:
            crawled_articles_file_path (_type_): _description_
            processed_articles_file_path (_type_): _description_
            total (int, optional): _description_. Defaults to 0.
            step (int, optional): _description_. Defaults to 10.
        """    
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
            processed_articles = self._process_articles(processing_articles)
            
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

    def _process_articles(self, articles_to_process):
        """Crawl list các articles

        Args:
            articles_to_process (list): List các articles cần crawl (mới chỉ có đường dẫn, thời gian đăng, tiêu đề)

        Returns:
            list: List các articles đã crawl hoàn chỉnh
        """        
        processed_articles = []
        for article in articles_to_process:
            try:
                article.process_url()
                processed_articles.append(article)
            except Exception as e:
                self.excluded_articles.append(article)
                print(f'ERROR processing article: {type(e).__name__}: {article.url}. Added to excluded articles')
        return processed_articles

    def filter_articles(self, processed_submaps_file_path, output_folder_path, filtered_output_folder_path, wanted_categories):
        """Lọc các articles đã crawl về theo chủ đề quan tâm

        Args:
            processed_submaps_file_path (str): Đường dẫn tới file .txt lưu trữ các submap đã xử lý
            output_folder_path (str): đường dẫn tới folder chứa các file .txt lưu trữ các articles hoàn chỉnh
            filtered_output_folder_path (str): đường dẫn tới folder chứa các file .txt lưu trữ các articles sau khi lọc chủ đề
        """        
        processed_submaps = self.get_articles(processed_submaps_file_path)
        submaps_path_to_process = []
        for submap in processed_submaps:
            extracted_name, _, processed_name = self._get_file_name_from_submap(submap)
            processed_articles_file_path =  output_folder_path + processed_name
            filtered_articles_file_path = filtered_output_folder_path + extracted_name + '_filtered.txt'
            submaps_path_to_process.append([processed_articles_file_path, filtered_articles_file_path])

        excluding = ['Doanh nghiệp giới thiệu']

        for submap_to_process in submaps_path_to_process:
            filtered_articles = []
            procesed_articles_path = submap_to_process[0]
            save_path = submap_to_process[1]
            articles = self.get_articles(procesed_articles_path)

            for article in articles:
                if ArticleManagers._contains_text(article.categories, wanted_categories) and not ArticleManagers._contains_text(article.categories, excluding):
                    filtered_articles.append(article)
            self.save_articles(filtered_articles, save_path)

    def get_articles(self, file_path):
        """Tạo list các articles từ file lưu trữ

        Args:
            file_path (str): ĐĐường dẫn tới file .txt

        Returns:
            list: List các articles trong file đó
        """        
        articles = []
        try:
            with open(file_path, "r", encoding= 'utf-8') as file:
                for line in file:
                    try:
                        line = Articles._linify_text(line)
                        article = Articles._from_line(line)
                        if 'http' in article.url:
                            articles.append(article)
                    except Exception as e:
                        print(f'ERROR getting articles: {type(e).__name__} from {file_path}')
            print(f'Finished file {file_path}, got {len(articles)} articles.')
        except FileNotFoundError:
            print(f'Articles file not found at: {file_path}')
        return articles
    
    def save_articles(self, articles, file_path, mode = 'w', encoding = 'utf-8'):
        """Lưu list các articles vào 1 file

        Args:
            articles (list): List các articles cần ghi
            file_path (str): Đường dẫn tới file .txt
            mode (str, optional): Chế độ mở file .txt. Defaults to 'w'.
            encoding (str, optional): Loại encoding. Defaults to 'utf-8'.
        """        
        with open(file = file_path, mode = mode, encoding = encoding) as file:
            for article in articles:
                file.write(str(article))
                file.write("\n")
    
    # Các helper functions

    @classmethod
    def _remove_duplicate_urls(cls, file_path):
        """Loại bỏ các articles trùng đường dẫn trong cùng 1 file .txt

        Args:
            file_path (str): Đường dẫn tới file .txt
        """        
        unique_urls = set()
        articles = cls.get_articles(file_path=file_path)
        for article in articles:
            pre_adding_length = len(unique_urls)
            unique_urls.add(article.url)
            post_adding_length = len(unique_urls)
            if pre_adding_length == post_adding_length:
                articles.remove(article)
        cls.save_articles(articles= articles, file_path= file_path, mode = 'w')
    
    @classmethod
    def _get_file_name_from_submap(cls, submap):
        """Tạo tên file để lưu trữ submap đã xử lý và các articles đã crawl từ submap

        Args:
            submap (article): Object article của submap

        Returns:
            list: List gồm tên tách ra từ đường dẫn submap, tên để lưu file .txt các đường dẫn article đã crawl được, và tên để lưu các articles đã crawl hoàn chỉnh
        """        
        extracted_name = submap.url[submap.url.rfind("/") + 1:submap.url.rfind(".xml")]
        crawled_name = extracted_name + '.txt'
        processed_name = extracted_name + '_processed.txt'
        return extracted_name, crawled_name, processed_name

    @classmethod
    def _get_paths_from_submap(cls, submap, output_folder_path):
        """Lấy đường dẫn lưu trữ của submap (phục vụ bước lọc chủ đề theo yêu cầu)

        Args:
            submap (article): Object article của submap
            output_folder_path (str): Đường dẫn tới folder chứa dữ liệu đã crawl được

        Returns:
            list: List gồm đường dẫn tới file .txt lưu trữ các đường dẫn articles đã crawl, và file .txt lưu trữ các articles hoàn chỉnh đã crawl
        """        
        _, crawled_name, processed_name = ArticleManagers._get_file_name_from_submap(submap)
        crawled_articles_file_path = output_folder_path + crawled_name
        processed_articles_file_path = output_folder_path + processed_name
        return crawled_articles_file_path, processed_articles_file_path


    @classmethod
    def _get_iso_from_current_time(cls):
        """Kiểm tra thời gian submap được cập nhật (tránh xử lý 1 submap nhiều lần)

        Returns:
            datetime: Thời gian submap được cập nhật
        """        
        current_time = datetime.datetime.now()
        offset = datetime.datetime.now().astimezone().strftime("%z")
        colon_offset = offset[:-2] + ":" + offset[-2:]
        iso_time = current_time.strftime("%Y-%m-%dT%H:%M:%S") + colon_offset
        return iso_time

    def _process_urls_from_submaps(self, processed_submaps_file_path, output_folder_path):
        """Xử lý list các submaps: (1) Crawl tất cả các đường dẫn articles, và (2) crawl các articles từ đường dẫn

        Args:
            processed_submaps_file_path (str): Đường dẫn tới file .txt lưu trữ các submaps đã xử lý xong
            output_folder_path (str): Đường dẫn tới folder lưu trữ các submaps đã xử lý xong
        """        
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
            except Exception:
                last_processed = submap.last_processed
            if (last_processed == Articles.not_available) or (lastmod > last_processed):
                crawled_articles_file_path, processed_articles_file_path = ArticleManagers._get_paths_from_submap(submap, output_folder_path)
                self.process_and_save(crawled_articles_file_path, processed_articles_file_path)
                submap.last_processed = ArticleManagers._get_iso_from_current_time()
                self.save_articles(self.processed_submaps, processed_submaps_file_path, 'w')
                print(f'Finished processing {submap.url}.')
    
    @classmethod           
    def _contains_text(cls, text, word_list):
        """Kiểm tra chủ đề của article có nằm trong danh sách qua ntâm khồng

        Args:
            text (str): Chủ đề của bài báo
            word_list (str): List các chủ đề quan tâm

        Returns:
            bool: True nếu có và False nếu không
        """        
        for word in word_list:
            if word in text:
                return True
        return False

