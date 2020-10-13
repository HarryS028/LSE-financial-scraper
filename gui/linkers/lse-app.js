let {PythonShell} = require('python-shell')
var path = require("path")

function get_financials() {
    
    var input_file = document.getElementById("uploader").files[0].path

    var all = document.getElementById("All").checked
    var ratios = document.getElementById("Ratios").checked
    var balance = document.getElementById("Balance").checked
    var income = document.getElementById("Income").checked

    var check_status = [all, ratios, balance, income];
    
    var options = {
        scriptPath: path.join(__dirname, '/../engine/'),
        args: [input_file, check_status]
    }

    let pyshell = new PythonShell('test-engine.py', options);
    //var test_file = new python('test-engine.py', options);

    pyshell.on('message', function(message) {
        alert(message);
    })
    
    document.getElementById("uploader").value = "";
}

function scrape_financials() {

    document.getElementById("scrape-button").innerText = "Processing";

    var inputs = document.getElementById("uploader").files[0].path

    var all = document.getElementById("All").checked
    var ratios = document.getElementById("Ratios").checked
    var balance = document.getElementById("Balance").checked
    var income = document.getElementById("Income").checked

    var check_status = [all, ratios, balance, income]

    var options = {
        scriptPath: "C:/Users/Harry/Python/Financial_data_scraper/gui-app/engine/",
        args: [inputs, check_status]
    }
    //path.join(__dirname, '/../engine/')

    let pyshell = new PythonShell('LSE_scraper.py', options);

    pyshell.on('message', function(message) {
        alert(message);
    })
    
    document.getElementById("uploader").value = "";
    document.getElementById("scrape-button").value = "Scrape";
}

function toggle_checks() {

    if (document.getElementById("All").checked == true) {
        document.getElementById("All").checked = !document.getElementById("All").checked;
    };

}

function toggle_all() {
    
    if (document.getElementById("Ratios").checked == true) {
        document.getElementById("Ratios").checked = !document.getElementById("Ratios").checked;
    };
    if (document.getElementById("Balance").checked == true) {
        document.getElementById("Balance").checked = !document.getElementById("Balance").checked;
    };
    if (document.getElementById("Income").checked == true) {
        document.getElementById("Income").checked = !document.getElementById("Income").checked;
    };
}
