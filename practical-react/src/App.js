import React from 'react';

import{Cards , Charts ,Country } from './components';
import { fetchData } from './api';
import styles from './App.module.css';





class App extends React.Component {


    state = {
        data: {},
        country:'',
    } 
    async componentDidMount() {
        const fetcheddata = await fetchData();
    
        this.setState({ data : fetcheddata});
      }
    
    handleCountryChange = async (country)=>{

        console.log(country);
    }
      render(){
        const { data }= this.state;
        return(
            <div className={styles.container}> 
               <Cards data ={data} />
               
               <Charts />
               <Country  handleCountryChange={this.handleCountryChange}/>

            </div>
        )
    }
}
export default App;
