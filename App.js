import React from 'react';
import countryData from './component/countriesData';
import CountryCard from './component/CountryCard';  

function App() {
  return (
    <div className="App">
      <h1>Country Cards</h1>
      <div className="card-list">
        {countryData.map((country, index) => (
          <CountryCard key={index} country={country} />
        ))}
      </div>
    </div>
  );
}

export default App;
