import React, { Component } from 'react'
import { makeStyles, Paper, Grid, Container, TextField} from '@material-ui/core';

class Counter extends Component{
    constructor(props){
        super(props)
    }

    //On the change event for the select box pass the selected value back to the parent


    render(){
        let csrCount = this.props.csrCount;
        let ssdcCount = this.props.ssdcCount;

            return (
                <div><p></p>
                <b>
                </b>
                    <h4>Current CSRNet Count: {csrCount}</h4>
                    <h4>Current SSDCNet Count: {ssdcCount}</h4>
                </div>
        )
    }
}

export default Counter;