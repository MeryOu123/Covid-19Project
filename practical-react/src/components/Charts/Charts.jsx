import React , {useState,useEffect } from 'react';
import {Line , Bar } from 'react-chartjs-2';


import styles from './Charts.module.css';

const Charts = () => {
    const[dailydata , setdailydata]= useState([]);

useEffect(()=>{
    fetch("http://127.0.0.1:5000/chart_active_case").then(response=>
    response.json().then( data =>
         { setdailydata(data.result);
    })
    );
},[]
    
    
 
);

  
console.log(dailydata);
const dataa = dailydata.map((dailydata) => ({confirmed : dailydata.total_cases,
deaths :dailydata.total_deaths,
cured : dailydata.total_cured,
date :dailydata.Date,
}));
const lineChart = (
   dailydata.length
    ?( <Line data ={{
        labels :dataa.map(({date})=> date)
        ,
        datasets : [{
            data : dataa.map(({confirmed})=> confirmed),
            label:'Infected',
            borderColor:'#3333ff',
            fill: true,
        },
        {data : dataa.map(({deaths})=>deaths),
        label:'Deaths',
        borderColor:'red',
        backgroundColor:'rgba(255,0,0,0.5)',
        fill: true,},
        {data : dataa.map(({cured})=>cured),
        label:'Cured',
        borderColor:'green',
        backgroundColor:'rgba(0,255,0,0.5)',
        fill: true,}],
        
}
}
       />) : null
);

return (
        <div className={styles.container}>
            {lineChart}
        </div>
    )
}

export default Charts ;