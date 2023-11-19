const renderData = (source ,amount) =>{
    const ctx = document.getElementById('myChart').getContext('2d');
  
    new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: source,
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
          text: "Income per Source"
       }
      }
    });
  
  }
  
    const getChartData =() =>{
      fetch('/userincome/income-summary/')
      .then((res)=> res.json())
      .then((results) =>{
          console.log("results", results);
          const income_data = results.income_summary_data;
          if (Object.keys(income_data).length === 0) {
              console.log("No source data available.");
              return;
            }
          const source = Object.keys(income_data)
          const amount = Object.values(income_data).map(income => income.amount);
         
          renderData(source ,amount)
          });
      }
  
  
      
  
    window.onload = getChartData();