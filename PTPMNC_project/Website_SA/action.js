var username = "DS2023";
var password = "4A3E68AC";
var curPage = 1;
var totalPage = 1;
var dataTable = [];

window.onload = function() {
    const inputFrom = document.getElementById('input_from');
    const inputTo = document.getElementById('input_to');
    const ngayTao = document.getElementById('created_date');
    const currentDate = new Date();
    const currentYear = currentDate.getFullYear();
    const currentMonth = currentDate.getMonth() + 1; // Months are zero-indexed
    const currentDay = currentDate.getDate();

    const formattedDate = `${currentYear}-${currentMonth.toString().padStart(2, '0')}-${currentDay.toString().padStart(2, '0')}`;
    inputFrom.value = formattedDate;
    inputTo.value = formattedDate;
    ngayTao.value = formattedDate;
};

document.addEventListener("DOMContentLoaded", function() {
    // Adding click event listeners to each dashboard card
    var search = document.getElementById('search-summit');
    search.addEventListener('click', function () {
        curPage = 1;
        totalPage = 1;
        searchSubmit();

    });

    var nextPage = document.getElementById('search-next');
    nextPage.addEventListener('click', function () {
        if ((curPage +1 ) > totalPage) {
            showWarning('Đang ở trang cuối!');
            return;
        }
        curPage++;
        searchSubmit();
    });

    var prePage = document.getElementById('search-pre');
    prePage.addEventListener('click', function () {
        if (curPage  === 1) {
            showWarning('Đang ở trang đầu!');
            return;
        }
        curPage--;
        curPage = Math.max(curPage, 1)
        searchSubmit();
    });
    
    
    // function show btn next 
    function showBtnNext(){
        prePage.style.display = 'inline-block';
        nextPage.style.display = 'inline-block';
    }

    // function hide btn next 
    function hideBtnNext(){
        prePage.style.display = 'none';
        nextPage.style.display = 'none';
    }
    
    // sumit search request
    function searchSubmit() {
        let  stockCode = document.getElementById('input_stock_code').value;
        if(!stockCode) {
            showWarning('Mã chứng khoán không thể bỏ trống!');
            return;
        }
        let  label = document.getElementById('input_label').value;
        let  fromDate = document.getElementById('input_from').value;
        let  toDate = document.getElementById('input_to').value;
       
        if (fromDate > toDate) {
            showWarning('Thời gian băt đầu lớn hơn thời gian kết thúc!');
            return;
        }

        if (curPage > totalPage) {
            showWarning('Không tìm thấy dữ liệu!');
            return;
        }

        if (curPage < 1) {
            return;
        }

        (async () => {
            try {
                const stockData = await getStockInformation(stockCode, label, fromDate, toDate, curPage);
                
                if(stockData.data){
                    totalPage = Math.max(1, parseInt(stockData.totalPage) ?? 0)
                        
                    dataTable = stockData.data
                    dumpTable()
                    showSuccess(stockData.status)
                } else {
                    dataTable = [];
                    showWarning(stockData.status);
                }

                if(totalPage > 1){
                    showBtnNext()
                }else {
                    hideBtnNext()
                }
          
            } catch (error) {
                console.error('An error occurred:', error);
            }
        })();
    }
    
    // dump data to table
    // Function to add a new row to the table
    function dumpTable() {
        // xoa data cu
        const table = document.querySelector('.table-dashboard'); // Get the table element

        // Get all rows (including header)
        const rows = table.querySelectorAll('tr');

        // Skip the first row (header) and remove the rest
        for (let i = 1; i < rows.length; i++) {
            rows[i].remove();
        }
        
        // fill data moi
        dataTable.forEach(function(rowData, index) {
            let backgroundColor = 'a';

            if (index % 2) {
                backgroundColor = 'background-color-row-gray';
            }

            var newRow = table.insertRow();
            
            var cell1 = newRow.insertCell();
            cell1.textContent = rowData.stock_code;
            cell1.classList.add(backgroundColor)
            
            var cell2 = newRow.insertCell();
            const anchorElement = document.createElement('a');
            anchorElement.href = rowData.article; // Cài đặt thuộc tính href
            anchorElement.target = '_blank'; // Cài đặt thuộc tính target
            anchorElement.textContent = rowData.article;
            cell2.appendChild(anchorElement);
            cell2.classList.add(backgroundColor)

            var cell3 = newRow.insertCell();
            cell3.textContent = rowData.created_date;
            cell3.classList.add(backgroundColor)
            
            var cell4 = newRow.insertCell();
            cell4.textContent = rowData.label;
            let textColor = getClasTextByLabel(rowData.label);
            cell4.classList.add(textColor)
            cell4.classList.add(backgroundColor)
            
            var cell5 = newRow.insertCell();
            cell5.textContent = rowData.content;
            cell5.classList.add(backgroundColor)
        });
    }

    function getClasTextByLabel(label){
        if (label === 'blank')
            return 'blank-color';
        if (label === 'neutral')
            return 'neutral-color';
        if (label === 'positive')
            return 'positive-color';
        if (label === 'negative')
            return 'negative-color';

        return '';
    }
    
    //function get data by api search
    async function getStockInformation(stockCode, label, fromDate, toDate, page = 1, pageSize = 10) {
        return new Promise((resolve, reject) => {

            const url = new URL('https://sentiment-analytics.azurewebsites.net/api/get-stock-information',);

            url.searchParams.append('stock_code', stockCode);
            url.searchParams.append('from_date', fromDate);
            url.searchParams.append('to_date', toDate);
            url.searchParams.append('page', page);
            url.searchParams.append('pageSize', pageSize);

            if(label) {
                url.searchParams.append('label', label);
            }
            
            // Tạo XMLHttpRequest object
            const xhr = new XMLHttpRequest();

            // Mở request
            xhr.open('GET', url, true);
            
            // Set headers
            xhr.setRequestHeader('Accept', 'application/json'); // Request JSON response
            xhr.setRequestHeader('Content-Type', 'application/json'); // Optional, if the API expects JSON data
            xhr.setRequestHeader('Cache-Control', 'no-cache'); // Set cache control for fresh data
            xhr.setRequestHeader('username', 'DS2023');
            xhr.setRequestHeader('password', '4A3E68AC');

            // Set response type
            xhr.responseType = 'json';

            // Define callback function for when the request is complete
            xhr.onload = function() {
                if (xhr.status === 200) {
                    // Resolve the promise with the response data
                    resolve(xhr.response);
                } else {
                    // Reject the promise with an error message
                    reject(new Error('Error:', xhr.statusText));
                }
            };

            // Send the request
            xhr.send();
        });
    }

    // show warning
    function showWarning(message) {
        const warningContainer = document.getElementById('warning-container');
        // close old warning
        closeWarning()
        const warningMessage = document.querySelector('.warning-message');

        warningMessage.textContent = message;
        warningContainer.style.display = 'block';

        // Automatically close the warning after 1 second
        setTimeout(() => {
            warningContainer.style.display = 'none';
        }, 2000);
    }

    // show success
    function showSuccess(message) {
        const warningContainer = document.getElementById('success-container');
        // close old warning
        closeWarning()
        const warningMessage = document.querySelector('.success-message');

        warningMessage.textContent = message;
        warningContainer.style.display = 'block';

        // Automatically close the warning after 1 second
        setTimeout(() => {
            warningContainer.style.display = 'none';
        }, 2000);
    }
    
    function closeWarning() {
        const warningContainer = document.getElementById('warning-container');
        warningContainer.style.display = 'none';
    }
    
    // // import data

    const downloadButton = document.getElementById('downloadButton');
    const uploadButton = document.getElementById('uploadButton');
    const fileInput = document.getElementById('fileInput');

    downloadButton.addEventListener('click', () => {
        // Replace 'https://example.com/file.pdf' with the actual file URL
        const fileURL = 'file/Template_input.xlsx';

        // Create a new link element
        const downloadLink = document.createElement('a');
        downloadLink.href = fileURL;
        downloadLink.download = 'file.xlsx'; // Set filename for download

        // Trigger the click event to initiate the download
        downloadLink.click();

        // Remove the link element after download
        downloadLink.remove();
    });

    uploadButton.addEventListener('click', () => {
        fileInput.click(); // Trigger file selection dialog
    });

    fileInput.addEventListener('change', (event) => {
        const file = event.target.files[0]; // Get the selected file

        // Check if a file is selected
        if (file) {
            // Handle file upload here (e.g., send to a server)
            UploadFile()
        }
    });

    // submit form
    var createdSubmit = document.getElementById('created_submit');
    createdSubmit.addEventListener('click', function () {
        createdByForm()
    });
    
    // tao ban ghi bang form 
    function  createdByForm() {
        let item = [{
            'article': document.getElementById('article').value,
            'created_date': document.getElementById('created_date').value,
            'content': document.getElementById('created_content').value,
        }];
        (async () => {
            try {
                
                const insertRow = await insertArticle(item);
                
            } catch (error) {
                console.error('An error occurred:', error);
            }
        })();
    }

    function validateInsertData(data) {
        if( !data.article  ) {
            showWarning('Thiếu trường link bài báo!');
            return;
        }
        data.id = data.article;

        if (!data.created_date) {
            showWarning('Thiếu trường ngày tạo!');
            return;
        }

        if (!data.content) {
            showWarning('Thiếu trường nội dung bài báo!');
            return;
        }
        return data; 
    }

    //function get data by api search
    async function insertArticle(data) {
        let insertData = [];
        data.forEach(function(rowData, index) {
           let tmpData = validateInsertData(rowData);
           if(tmpData){
               insertData.push(tmpData);
           }
           
        });
        if(!insertData.length){
            return ;
        }

        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();

            // Set up the request
            xhr.open('POST', 'https://sentiment-analytics.azurewebsites.net/api/insert-article-in-db', true);

            // Set headers
            xhr.setRequestHeader('username', 'DS2023');
            xhr.setRequestHeader('password', '4A3E68AC');
            xhr.setRequestHeader('Content-Type', 'application/json');

            // Define callback function for when the request is complete
            xhr.onload = function() {
                if (xhr.status === 200 || xhr.status === 201) { // Handle both created (201) and successful update (200) responses
                    const response = JSON.parse(xhr.responseText);
                    showSuccess('Thành công!');
                    // callModelAPI();
                    resolve(response);
                } else {
                    showWarning(insertRow.message);
                    reject(new Error('Error:', xhr.statusText));
                }
            };

            // Send the request with JSON data
            xhr.send(JSON.stringify(data));
        });
    }

    // // call api Model
    // function callModelAPI() {
    //     return new Promise((resolve, reject) => {
    //         const xhr = new XMLHttpRequest();
    //
    //         // Set up the request
    //         xhr.open('GET', 'https://sentiment-analytics.azurewebsites.net/api/model');
    //
    //         // Define callback function for when the request is complete
    //         xhr.onload = function() {};
    //
    //         // Send the request
    //         xhr.send();
    //     });
    // }

    // upload file xlsx
    function UploadFile() {
        var dataUpload = [];
        var regex = /^([a-zA-Z0-9\s_\\.\-:])+(.xls|.xlsx)$/;
        if (regex.test(fileInput.value.toLowerCase())) {
            if (typeof (FileReader) != "undefined") {
                var reader = new FileReader();
                if (reader.readAsBinaryString) {
                    reader.onload = function (e) {
                        dataUpload = ProcessExcel(e.target.result);
                    };
                    reader.readAsBinaryString(fileInput.files[0]);
                } else {
                    reader.onload = function (e) {
                        var data = "";
                        var bytes = new Uint8Array(e.target.result);
                        for (var i = 0; i < bytes.byteLength; i++) {
                            data += String.fromCharCode(bytes[i]);
                        }
                        dataUpload = ProcessExcel(data);
                    };
                    reader.readAsArrayBuffer(fileInput.files[0]);
                }
            } else {
                alert("This browser does not support HTML5.");
            }
        } else {
            alert("Please upload a valid Excel file.");
        }

    };

    function ProcessExcel(data) {
        var workbook = XLSX.read(data, {
            type: "binary"
        });
        var firstSheet = workbook.SheetNames[0];
        var excelRows = XLSX.utils.sheet_to_row_object_array(workbook.Sheets[firstSheet]);
        let insertData = []
        excelRows.forEach(function(rowData, index) {
            console.log(rowData)
            let item = {
                'article': rowData.URL,
                'created_date': rowData.Created_date,
                'content': rowData.Content,
            };
            insertData.push(item);
     
        });
        
        (async () => {
            try {
                const insertRow = await insertArticle(insertData);
            } catch (error) {
                console.error('An error occurred:', error);
            }
        })();
        return ;
        
    };
});
