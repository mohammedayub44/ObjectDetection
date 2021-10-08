import React from "react";
import ReactPlayer from 'react-player'
import captureVideoFrame from 'capture-video-frame'
import { findDOMNode } from 'react-dom'
import styles from './Player.css';
import LineGraph from './Graph'
import occupancyData from './Data'
import DynamicSelect from './Occupancy'
import Counter from './Counter'
import {Row, Button, Form, FormControl, InputGroup, Navbar, Nav} from 'react-bootstrap';
import screenfull from 'screenfull'
import { makeStyles, Paper, Grid, Container, TextField} from '@material-ui/core';
import logo from './logo_fprf.png'


const axios = require('axios').default;
const occData = occupancyData.occupancyData
console.log(occData)
const base64Header = 'data:image/gif;base64,';
const classes = makeStyles(theme => ({
root: {
  flexGrow: 1
}
}));

export default class Player extends React.Component {
constructor (props) {
  super(props)
  this.state = {
    url: "https://crowd-counter-test-vids.s3.us-east-2.amazonaws.com/IMG_1852.MOV",
    playing: false,
    image: null,
    frames: [],
    counts: [],
    played: 0,
    duration: 0,
    captureTime: [],
    captureInterval: 2000, 
    isLoading: false, 
    result: 0,   
    heatmaps: [],
    heatmap: 'R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs=',
    crowdclass: "", 
    selectedValue: 'Nothing selected',
    area: 0,
    unit: 'm2',
    occLoadFactor:0,
    threshold: 0,
    thresholds:[],
    ssdcnet:[], 
    averages: [], 
    ip: window.location.hostname
  }
  //this.handleChange = this.handleChange.bind(this);
  this.captureVideo = this.captureVideo.bind(this);
  this.handleChange = this.handleChange.bind(this);
  this.handleSubmit = this.handleSubmit.bind(this);
  this.forceUpdateHandler = this.forceUpdateHandler.bind(this);
  this.autoCapture = this.autoCapture.bind(this);
  this.stopAutoCapture = this.stopAutoCapture.bind(this);
  this.handleSelectChange = this.handleSelectChange.bind(this);
  this.onChange = this.onChange.bind(this)
}

forceUpdateHandler(){
  this.forceUpdate();
};

onChange(e){
  const re = /^[0-9\b]+$/;
  if (e.target.value === '' || re.test(e.target.value)) {
     this.setState({area: e.target.value})
  };
  
}

setUnits(event) {
  this.setState({unit: event.target.value});
  console.log(event.target.value);
}

handleChange(event) {
  this.setState({value: event.target.value});
}

handleSelectChange = (selectedValue) => {
  this.setState({
      selectedValue: selectedValue
  });   
}

handleSubmit(event) {
  event.preventDefault();
  console.log('A video was submitted: ' + this.state.value);
  
}

handleSeekMouseDown = e => {
  this.setState({ seeking: true })
}

handleSeekChange = e => {
  this.setState({ played: parseFloat(e.target.value) })
}

handleSeekMouseUp = e => {
  this.setState({ seeking: false })
  this.player.seekTo(parseFloat(e.target.value))
}

handleProgress = state => {
  console.log('onProgress', state)
  // We only want to update time slider if we are not currently seeking
  if (!this.state.seeking) {
    this.setState(state)
  }
}

handleEnded = () => {
  console.log('onEnded')
  this.setState({ playing: false });
  if (this.state.intervalId){
  clearInterval(this.state.intervalId);
}
}

handleDuration = (duration) => {
  console.log('onDuration', duration)
  this.setState({ duration })
}

handleCaptureInterval(event) {
  
  this.setState({captureInterval: event.target.value});
  console.log("2", this.state.captureInterval)
}


captureVideo() {
  const frame = captureVideoFrame(this.player.getInternalPlayer());
  console.log('captured frame', frame);
  this.setState({ image: frame.dataUri });
  let image_data = frame.dataUri;
  this.state.frames.push(image_data);
  let times = this.state.duration * this.state.played;
  let ip = ''.concat('http://', this.state.ip, ':8081/predict');
  console.log(ip);
  this.state.captureTime.push(times.toFixed(2));

    
  const imgData = frame.dataUri;
  
  let metadata = { vidUrl: this.state.url, occType: this.state.selectedValue, area: this.state.area, 
                    units: this.state.unit, duration: this.state.duration, threshold: this.state.threshold }
  var data = imgData.split(",");
  var payload = {
    header: data[0],
    data: data[1], 
    metadata: metadata
  };
  console.log('sending to server', payload);

  axios.post(ip, payload)
  .then((res) => {
    console.log("RESPONSE RECEIVED: ", res);
    this.setState({result:res.data.predictions.count});
    this.setState({heatmap:res.data.predictions.predicted_heatmap});
    this.setState({crowdclass:res.data.predictions.class});
    this.state.averages.push(res.data.predictions.average)
    this.state.counts.push(this.state.result);
    this.state.ssdcnet.push(res.data.predictions.ssdcnet_count);
    this.state.heatmaps.push(base64Header+res.data.predictions.predicted_heatmap);
    this.state.thresholds.push(this.state.threshold)
    this.forceUpdateHandler();
    console.log('heatmaps', this.state.heatmaps);
    console.log(this.state.counts);
  })
  .catch((err) => {
    console.log("AXIOS ERROR: ", err);
  });
}

autoCapture() {
  let intervalId = setInterval(this.captureVideo, this.state.captureInterval);
  this.setState({ intervalId: intervalId });
}

stopAutoCapture() {
  clearInterval(this.state.intervalId);
}

handleClickFullscreen = () => {
  screenfull.request(findDOMNode(this.player));
}

ref = player => {
  this.player = player;
}

handleCancelClick = (event) => {
  this.setState({ result: "" });
  this.setState({ image: null });
  this.setState({ crowdclass: "" });
  this.setState({ heatmap: ""});
}

render() {
  //const isLoading = this.state.isLoading;
  const { played } = this.state;
  let captures = this.state.frames;
  const result = occData.find( element => element.Use===this.state.selectedValue );
  const area = this.state.area;
  let threshold = 0;
  let thresholds = [];

  if (result && this.state.unit === 'm2') {
    threshold = this.state.area / result.m2;
   } 

  if (result && this.state.unit === 'ft2') {
    threshold = this.state.area / result.ft2;
  } 

  if (captures){
    var i;
    for (i = 0; i < captures.length; i++) {
      thresholds.push(threshold);
    }
  console.log(captures.length);
  console.log(threshold)
  console.log(thresholds)
  }
  return (
    
    <div className="root">
     
     <Navbar expand="xl" className="navbar" bg="dark" variant="dark">
     
    <Navbar.Brand href="#home">
      <img
        alt=""
        src={logo}
        width="165"
        height="60"
        className="d-inline-block align-top"
      />{' '}
    </Navbar.Brand><h1>Crowd Counting Application</h1>
  </Navbar>
    
    <Grid container spacing={3}>
      <Grid className='content' item xs={6}>
        <Paper className='quadrant'>
        <InputGroup className="content"><h2 >Controls</h2>        
          <div><br/><h5>Enter a custom video URL:</h5></div>
          <div style={{display:'flex'}}>
           <FormControl 
            ref={input => { this.urlInput = input }} type='text'
            placeholder="Enter a video URL"
            aria-label="Video URL"
            aria-describedby="basic-addon2"
            onSubmit={this.handleSubmit}/>
            <Button className='Button' onClick={() => this.setState({ url: this.urlInput.value })}>Load</Button><br/>
          </div>

            <DynamicSelect className='content' arrayOfData={occData} onSelectChange={this.handleSelectChange} /> <br />


        <h5>Enter area of Video Feed:</h5>
          <FormControl 
          type='number'
          pattern='[0-9]{0,5}'
          placeholder="Enter area of Video Feed"

          value={this.state.area}
          onChange={this.onChange}
          />

          
      <div onChange={this.setUnits.bind(this)}><h5>Units of Measure:</h5>
      <div>   
        <input type="radio" value="m2" defaultChecked name="Units of Measure"/> Metric (m²)       
        <input type="radio" value="ft2" name="Units of Measure"/> Imperial (ft²)</div>
      </div>

          </InputGroup></Paper>
      </Grid>
      <Grid item xs={6} className={styles.details}>
        <Paper className='quadrant'><h2>Environment Details</h2>
        {
          this.state.url !== undefined &&
          <div>
              <b>Video Source URL: </b>{this.state.url}
            </div>
          }{"\n"}
          {          <div>
              <b>Camera Feed Area (m²/ft²): </b>{this.state.area + ' '}{this.state.unit}
            </div>}{"\n"}

            <div><b>
              Selected Occupancy Type:</b> {this.state.selectedValue}</div>
        {
          result !== undefined && 
            <div>
              <b>Occupancy Loads (per person): </b>{result.ft2} Ft²; {result.m2} m²
            </div>
                  }
                  {"\n"}
                  {
        result !== undefined && 
      <div><b>Occupancy Threshold: </b> {threshold.toFixed(0)}</div> 
      } <Counter csrCount={this.state.counts.slice(-1)[0]} ssdcCount={this.state.ssdcnet.slice(-1)[0]}></Counter></Paper>
      </Grid>
      {
          result !== undefined && area !== 0 &&
      <Grid item xs={6}>
        <Paper className='quadrant'>
        <h2>Video Feed</h2>
        <Row className="content">
          
          <ReactPlayer 
            ref={player => { this.player = player }}
            url={this.state.url}
            playing={this.state.playing}
            onSeek={e => console.log('onSeek', e)}
            onProgress={this.handleProgress}
            onDuration={this.handleDuration}
            onEnded={this.handleEnded}
            width='100%'
            height='100%'
            config={{ file: { attributes: {
              crossorigin: 'anonymous'
            }}}}
          />
            <input className='content' width='100%'
                      type='range' min={0} max={1} step='any'
                      value={played}
                      onMouseDown={this.handleSeekMouseDown}
                      onChange={this.handleSeekChange}
                      onMouseUp={this.handleSeekMouseUp}
                    />
      <Row >
        <Button variant='control' onClick={() => this.setState({ playing: true })}>Play</Button>
        <Button variant='control' onClick={() => this.setState({ playing: false })}>Pause</Button>
        <Button variant= 'control' onClick={this.handleClickFullscreen}>Fullscreen</Button>
        <Button variant='control' onClick={this.captureVideo}>Capture Frame</Button>
      </Row>
      <Row><p></p>
        <label>
        Pick frame capture interval:
          <select value={this.state.captureInterval} onChange={this.handleCaptureInterval.bind(this)}>
            <option value="1000">1 second</option>
            <option value="2000">2 seconds</option>
            <option value="5000">5 seconds</option>
            <option value="10000">10 seconds</option>
            <option value="30000">30 seconds</option>
            <option value="60000">1 minute</option>
          </select>
        </label>
      </Row>
      <Row>
        <Button variant='control' onClick={this.autoCapture}>AutoCapture</Button>
        <Button variant='control' onClick={this.stopAutoCapture}>StopCapture</Button>
      
      </Row>
    </Row></Paper>
      </Grid>}
      {
          result !== undefined &&  area !== 0 &&
               <Grid item xs={6}><Paper className='quadrant'>
                 <h2>Model Prediction Count Over Time </h2>
        <LineGraph data={this.state.counts} labels={this.state.captureTime} 
        ssdcnet={this.state.ssdcnet} average={this.state.averages} 
        threshold={thresholds} size={[500,500]}/>
      </Paper></Grid>}
   
      <Grid item xs={12}>
        { captures.length > 0 &&
          <div ><h2>Captures</h2>
            {captures.length > 0 && 
          
            this.state.frames.map((item,index) => (
            <Paper variant="outlined" elevation={2}>
          <div className="themed-container">
          <h4>Elapsed Time: {this.state.captureTime[index]} (in seconds)<br/>
          CSRNet Count: {this.state.counts[index]}<br/>
          SSDCNet  Count: {this.state.ssdcnet[index]}<br/>
          Average Count: {this.state.averages[index]}</h4>
           </div>
      
          <img src={item} alt='capture' width="640" height="480"/>
          <img src={this.state.heatmaps[index]} alt='heatmap' width="640" height="480"/></Paper>          
        ))}
          </div>
}
      </Grid>
      
    </Grid>
  </div>
    
  );
}
}
