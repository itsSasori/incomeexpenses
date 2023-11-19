const renderData = (category ,amount) =>{
  const ctx = document.getElementById('myChart').getContext('2d');

  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: category,
      datasets: [{
        label: '',
        data: amount,
        backgroundColor: [
            "rgba(255, 99, 132, 0.2)",
            "rgba(54, 162, 235, 0.2)",
            "rgba(255, 206, 86, 0.2)",
            "rgba(75, 192, 192, 0.2)",
            "rgba(153, 102, 255, 0.2)",
            "rgba(255, 159, 64, 0.2)",
          ],
          borderColor: [
            "rgba(255, 99, 132, 1)",
            "rgba(54, 162, 235, 1)",
            "rgba(255, 206, 86, 1)",
            "rgba(75, 192, 192, 1)",
            "rgba(153, 102, 255, 1)",
            "rgba(255, 159, 64, 1)",
          ],
        borderWidth: 1
      }]
    },
    options: {
     title:{
        display:true ,
        text: "Expenses per category"
     }
    }
  });

}

  const getChartData =() =>{
    console.log('Fetching');
    fetch('/expense-summary')
    .then((res)=> res.json())
    .then((results) =>{
        console.log("results", results);
        const category_data = results.expense_category_data;
        if (Object.keys(category_data).length === 0) {
            console.log("No expense data available.");
            return;
          }
        const category = Object.keys(category_data)
        const amount = Object.values(category_data).map(category => category.amount);
       
        
        renderData(category ,amount)
        });
    }


    

  window.onload = getChartData();