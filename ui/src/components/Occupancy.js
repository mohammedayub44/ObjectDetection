import React, {Component} from 'react';
import {Form, Label, Control} from 'react-bootstrap';

class DynamicSelect extends Component{
    constructor(props){
        super(props)
    }

    //On the change event for the select box pass the selected value back to the parent
    handleChange = (event) =>
    {
        let selectedValue = event.target.value;
        this.props.onSelectChange(selectedValue);
    }

    render(){
        let occupancyData = this.props.arrayOfData;
        let options = occupancyData.map((data) =>
                <option 
                    key={data.Use}
                    value={data.Use}
                >
                    {data.Use}
                </option>
            );
        
            return (
            <Form.Group controlId="exampleForm.ControlSelect1" onChange={this.handleChange} >
                <Form.Label><h5>Select Occupancy Type</h5></Form.Label>
                <Form.Control as='select'>
                <option default selected>--SELECT AN OPTION--</option>
                {options}
                </Form.Control>
                </Form.Group>
        )
    }
}

export default DynamicSelect;