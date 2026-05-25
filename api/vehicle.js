// api/vehicle.js - No fake data version
const keys = {
  "Introspection": { name: "Introspection", expires: "2050-12-31" }
};

const DEVELOPER = "@Introspection007";
const UKRAINE_API = "https://ukrainexinfo-vehicle-advance.42web.io/gateway.php";
const UKRAINE_KEY = "Tushar1demo";

function cleanValue(val) {
  if (!val || val === "" || val === "--") return "N/A";
  return String(val);
}

// ONLY known vehicles - no fake generation
const knownVehicles = {
  "GJ14X4555": {
    Owner_Name: "RAHUL MEHTA", Father_Name: "SURESH MEHTA",
    Registration_Number: "GJ14X4555", Make_Name: "HONDA",
    ModelName: "ACTIVA 6G", Color: "PEARL SPARKLE BLACK",
    Fuel_Type: "PETROL", Vehicle_Class: "TWO WHEELER",
    Registration_Date: "15-03-2023"
  },
  "MH12AB1234": {
    Owner_Name: "SUSHIL KUMAR", Father_Name: "RAMESH KUMAR",
    Registration_Number: "MH12AB1234", Make_Name: "MARUTI SUZUKI",
    ModelName: "SWIFT VXI", Color: "SOLID RED",
    Fuel_Type: "PETROL", Vehicle_Class: "FOUR WHEELER",
    Registration_Date: "01-01-2022"
  }
};

async function tryUkraineAPI(regNo) {
  try {
    const url = `${UKRAINE_API}?key=${UKRAINE_KEY}&Fuckreg=${regNo}`;
    const response = await fetch(url, { headers: { 'User-Agent': 'Mozilla/5.0' } });
    if (response.ok) {
      const data = await response.json();
      if (data && data.status === true) return { success: true, data: data };
    }
  } catch (error) {}
  return { success: false };
}

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Content-Type', 'application/json');
  
  let key = req.query.key;
  let regNo = req.query.Fuckreg || req.query.rc;
  
  if (!key) {
    return res.status(400).json({ status: false, message: "API key missing. Use ?key=Introspection" });
  }
  
  if (!keys[key]) {
    return res.status(401).json({ status: false, message: "Invalid API key" });
  }
  
  if (!regNo) {
    return res.status(400).json({ status: false, message: "Registration number missing" });
  }
  
  regNo = regNo.toUpperCase().trim();
  
  // Try Ukraine API first
  let result = await tryUkraineAPI(regNo);
  
  if (result.success && result.data) {
    return res.status(200).json(result.data);
  }
  
  // Check known vehicles database
  if (knownVehicles[regNo]) {
    const v = knownVehicles[regNo];
    return res.status(200).json({
      status: true,
      demo_mode: true,
      owner_information: {
        owner_name: v.Owner_Name,
        father_name: v.Father_Name
      },
      vehicle_details: {
        registration_number: v.Registration_Number,
        make: v.Make_Name,
        model: v.ModelName,
        color: v.Color,
        fuel_type: v.Fuel_Type,
        vehicle_class: v.Vehicle_Class
      },
      registration_details: {
        registration_date: v.Registration_Date
      }
    });
  }
  
  // Vehicle not found - return error, not fake data
  return res.status(404).json({
    status: false,
    message: "Vehicle not found in database",
    reg_number: regNo,
    developer: DEVELOPER
  });
}
