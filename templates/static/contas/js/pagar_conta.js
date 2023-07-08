function pagar_conta_button(id){
   

     fetch("/contas/pagar_conta/"+id, {
        method: 'GET',
        headers: {
            "Content-Type": "application/json",
            
        },
        body: JSON.stringify()
        
    }).then(function(result){
        return result.json()

    }).then(function(data){
        console.log(data)
        location.reload();
    })

}