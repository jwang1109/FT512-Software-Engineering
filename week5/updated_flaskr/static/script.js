try{
    /* button that ask if the user want to submit the page*/
    const button = document.querySelector('#submit');
    button.addEventListener("click",function(){
	bootbox.confirm({
	    message: 'Do you want to submit the page?',
	    buttons: {
		confirm: {
		    label: 'Yes',
		    className: 'btn-success'
		},
		cancel: {
		    label: 'No',
		    className: 'btn-danger'
		}
	    },
	    callback: function (result) {
		if(result){
		    bootbox.alert("Form submitted.");
		}else{
		    bootbox.alert("Action Cancelled.");
		}
	    }
	});
    })
    
    /* chart that display the time series of stock*/
    const selectedStock = document.querySelector("#stock-select");
    function plot(){
	d3.csv(`/static/stockdata/${selectedStock.value}.csv`, function(err, rows){
	    function unpack(rows, key) {
		return rows.map(function(row) { return row[key]; });
	    }
	    var trace1 = {
		type: "scatter",
		mode: "lines",
		name: `${selectedStock.value}-Close`,
		x: unpack(rows, 'Date'),y: unpack(rows, 'Close'),
		line: {color: '#17BECF'}}
	    var data = [trace1];
	    var layout = {
		title: `${selectedStock.value}`,
	    };
	    Plotly.newPlot('chart', data, layout);
	})
    }
    selectedStock.addEventListener("change",plot);
}catch(error){
    console.error(error);
}
