$(document).ready(function() {
    let totalcalories = $('#totalcalories').val();
    function updateCalories() {
        totalcalories = $('#totalcalories').val()
        $('#totalcarbs').val(`${Math.round(totalcalories*.60/4*10)/10}`)
        $('#totalproteins').val(`${Math.round(totalcalories*.20/4*10)/10}`)
        $('#totalfats').val(`${Math.round(totalcalories*.20/9*10)/10}`)
    }
    function updateMacros() {
        let newCalories = $('#totalproteins').val() * 4 + $('#totalcarbs').val() * 4 + $('#totalfats').val() * 9;
        $('#totalcalories').val(`${Math.round(newCalories*10)/10}`)
    }

    $(document).on("change, keyup", "#totalcalories", updateCalories)
    $(document).on("change, keyup", "#totalproteins", updateMacros)
    $(document).on("change, keyup", "#totalfats", updateMacros)
    $(document).on("change, keyup", "#totalcarbs", updateMacros)
    
    $("#generateButton").click(function(){
        $("#generateButton").html("Generating...")
    })
    async function updateSearch() {
        let query = $('#searchInput').val();
        // const response = await axios({
        //     method: "GET",
        //     url: 'https://api.spoonacular.com/recipes/autocomplete',
        //     data: {'type':'breakfast', 'query': `${query}` , 'number':'10', 'apiKey' :'d335708b957146b3b5888320ab83ffbe'}
        // })
        //  make call to python view function. dont mess with autocomplete.
        const response = await axios.get('https://api.spoonacular.com/recipes/autocomplete', {params: {type: 'breakfast', apiKey: 'd335708b957146b3b5888320ab83ffbe', number:'10'}})
        console.log(response.data)
    }

    $(document).on("change, keyup", "#searchInput", updateSearch)
}
)