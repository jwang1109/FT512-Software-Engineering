try{
    /* button that ask if the user want to submit the page*/
    const button = document.querySelector('#submit');
    button.addEventListener("click",function(event){
	event.preventDefault();
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
}catch(error){
    console.error(error);
}
