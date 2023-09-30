

try{
const button = document.querySelector('#go_duke');
const number = document.querySelector('#number')

button.addEventListener("click",function(){
    let curr = parseInt(number.innerHTML);
    number.innerHTML = curr+1;
});
}catch(error){
    console.error(error);
}




