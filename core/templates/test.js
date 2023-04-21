let genderInput = document.querySelectorAll(".gender");
let result = document.querySelector('.result');
let whoAmI;
for(let g of genderInput){
  if(g.checked)
    whoAmI = g.value;
}

function handleClick(el) {
  whoAmI = el.value;
  result.innerHTML = whoAmI;
}

console.log(whoAmI);
result.innerHTML = whoAmI;