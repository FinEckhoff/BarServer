
function sendOrder(orderList, barID) {
    if(orderList.length === 0){
        return;
    }
     json = JSON.parse(orderList)

     fetch('/api/submitOrder',
        {method: 'GET' }
    )
    delete json

}
