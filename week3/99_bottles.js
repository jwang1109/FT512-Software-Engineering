for(let n = 99; n>0; n--){
    if(n>1){
	console.log(`${n} bottles of beer on the wall, ${n} bottles of beer.`);
	if(n>2){
	    console.log(`Take one down, pass it around, ${n - 1} bottles of beer on the wall.`);
	}else if (n>1) {
            console.log('Take one down, pass it around, 1 bottle of beer on the wall.');
	}
    }
    else if (n==1){
        console.log("1 bottle of beer on the wall, 1 bottle of beer.");
        console.log("Take one down, pass it around, no more beer on the wall!");        
    }
}
