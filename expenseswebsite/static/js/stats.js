const renderChart=(data,labels)=>{
    const ctx = document.getElementById('myChart').getContext("2d");
    const myChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Last 6 months expenses',
                    data: data,
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.2)', 
                        'rgba(54, 162, 235, 0.2)', 
                        'rgba(255, 206, 86, 0.2)', 
                        'rgba(75, 192, 192, 0.2)',
                        'rgba(153, 102, 255, 0.2)', 
                        'rgba(255, 159, 64, 0.2)'  
                    ],
                    borderColor: [
                        'rgba(255, 99, 132, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)',
                        'rgba(255, 159, 64, 1)'
                    ],
                    borderWidth: 1
                },
            ],
        },
        options: {
            title: {
                display: true,
                text: "Expenses per Category",
            },
        },
    });
};

const getChartData = () => {
    console.log("fetching");
    fetch('/expense_category_summary')
        .then(res => res.json())
        .then(results => {
            console.log('Fetched results:', results);

            // Correct the key to match the API response
            const category_data = results.expense_category_amount || {};

            // Ensure category_data is an object before using Object.keys and Object.values
            if (typeof category_data !== 'object' || category_data === null) {
                console.error('Invalid category_data:', category_data);
                return;
            }

            const [labels, data] = [
                Object.keys(category_data),
                Object.values(category_data),
            ];

            renderChart(data, labels);
        })
        .catch(error => {
            console.error('Error fetching chart data:', error);
        });
};

document.onload=getChartData();
