import React , {useState,useEffect } from 'react';
import { NativeSelect, FormControl } from '@material-ui/core';
import { Line, Bar } from 'react-chartjs-2';
import styles from './Country.module.css';
const Country = ({handleCountryChange}) => {

    const[contries , setcontries]= useState([]);

    useEffect(()=>{
    fetch("http://127.0.0.1:5000/top_15").then(response=>
    response.json().then( data =>
         { setcontries(data.result);
    })
    );
},[]
    
   
 
);
console.log(contries);
const countries  = contries.map((contries) => ({countries : contries.country,}));
const barChart = (
    contries.total_cases ? (
      <Bar
        data={{
          labels: ['Infected', 'Recovered', 'Deaths'],
          datasets: [
            {
              label: 'People',
              backgroundColor: ['rgba(0, 0, 255, 0.5)', 'rgba(0, 255, 0, 0.5)', 'rgba(255, 0, 0, 0.5)'],
              data: [contries.total_cases, contries.Total_recovered, contries.Total_deaths],
            },
          ],
        }}
      
      />
    ) : null
  );

    return (
        <FormControl className = {styles.formControl}>
            <NativeSelect defaultValue="" onChange={(e)=> handleCountryChange(e.target.value)}>
                
                {countries.map((country, i)=> <option key ={i} value = {country.countries}>{country.countries}</option> )}
            </NativeSelect>
          
           
        </FormControl>
        
        
       

    

    )
}

export default Country ;