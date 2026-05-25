// api/vehicle.js - Complete Working Version
// Developer: @Introspection007

const keys = {
  "Introspection": { name: "Introspection", expires: "2050-12-31", plan: "LIFETIME" },
  "Tushar1demo": { name: "Tushar", expires: "2026-05-25" },
  "ukrainebst": { name: "UkraineBST", expires: "2026-05-25" }
};

const DEVELOPER = "@Introspection007";
const FREE_API = "https://t.me/exportbot01";
const UKRAINE_API = "https://ukrainexinfo-vehicle-advance.42web.io/gateway.php";
const UKRAINE_KEY = "Tushar1demo";
const EXTERNAL_API = "https://api.paanel.shop/api/gateway.php";

function cleanValue(val) {
  if (!val || val === "" || val === "--" || val === null) return "N/A";
  return String(val);
}

function getDemoVehicleData(regNo) {
  const demoDB = {
    "GJ14X4555": {
      Owner_Name: "RAHUL MEHTA", Father_Name: "SURESH MEHTA",
      Registration_Number: "GJ14X4555", Make_Name: "HONDA",
      ModelName: "ACTIVA 6G", Color: "PEARL SPARKLE BLACK",
      Fuel_Type: "PETROL", Vehicle_Class: "TWO WHEELER",
      Registration_Date: "15-03-2023", Cubic_Capacity: "109.51 CC"
    },
    "MH12AB1234": {
      Owner_Name: "SUSHIL KUMAR", Father_Name: "RAMESH KUMAR",
      Registration_Number: "MH12AB1234", Make_Name: "MARUTI SUZUKI",
      ModelName: "SWIFT VXI", Color: "SOLID RED",
      Fuel_Type: "PETROL", Vehicle_Class: "FOUR WHEELER",
      Registration_Date: "01-01-2022", Cubic_Capacity: "1197 CC"
    }
  };
  
  if (demoDB[regNo]) return { ...demoDB[regNo], demo_mode: true };
  
  return {
    Owner_Name: `OWNER OF ${regNo}`,
    Father_Name: "REGISTERED OWNER",
    Registration_Number: regNo,
    Make_Name: "DEMO VEHICLE",
    ModelName: "STANDARD MODEL",
    Color: "BLACK",
    Fuel_Type: "PETROL",
    Vehicle_Class: "FOUR WHEELER",
    Registration_Date: "01-01-2023",
    Cubic_Capacity: "N/A",
    demo_mode: true,
    note: "Demo data - Real API unavailable"
  };
}

async function tryUkraineAPI(regNo) {
  try {
    const controller = new AbortController();
    setTimeout(() => controller.abort(), 10000);
    
    const url = `${UKRAINE_API}?key=${UKRAINE_KEY}&Fuckreg=${encodeURIComponent(regNo)}`;
    const response = await fetch(url, {
      signal: controller.signal,
      headers: { 'User-Agent': 'Mozilla/5.0' }
    });
    
    if (response.ok) {
      const data = await response.json();
      if (data && (data.status === true || data.status === "true")) {
        return { success: true, data: data };
      }
    }
  } catch (error) {
    console.log("Ukraine API failed:", error.message);
  }
  return { success: false };
}

async function tryExternalAPI(regNo) {
  try {
    const controller = new AbortController();
    setTimeout(() => controller.abort(), 10000);
    
    const url = `${EXTERNAL_API}?key=Fuckedvehicle&Fuckreg=${encodeURIComponent(regNo)}`;
    const response = await fetch(url, {
      signal: controller.signal,
      headers: { 'User-Agent': 'Mozilla/5.0' }
    });
    
    if (response.ok) {
      const data = await response.json();
      if (data && data.success === true) {
        return { success: true, data: data };
      }
    }
  } catch (error) {
    console.log("External API failed:", error.message);
  }
  return { success: false };
}

function formatRealResponse(apiData, keyData, regNo) {
  let d = apiData.data || apiData;
  let fl = d.FastlaneResponse_Obj || {};
  
  return {
    status: true,
    source: "real_api",
    api_info: { key_used: keyData.name, valid_till: keyData.expires, developer: DEVELOPER },
    owner_information: {
      owner_name: cleanValue(d.Owner_Name),
      father_name: cleanValue(d.Father_Name),
      mobile_number: cleanValue(fl.rc_mobile_no),
      present_address: cleanValue(fl.rc_present_address)
    },
    vehicle_details: {
      registration_number: cleanValue(d.Registration_Number),
      make: cleanValue(d.Make_Name),
      model: cleanValue(d.ModelName),
      color: cleanValue(d.Color),
      fuel_type: cleanValue(d.Fuel_Type),
      vehicle_class: cleanValue(d.Vehicle_Class),
      chassis_number: cleanValue(d.Chassis_Number),
      engine_number: cleanValue(d.Engin_Number)
    },
    registration_details: {
      registration_date: cleanValue(d.Registration_Date),
      rto_name: cleanValue(d.RTO_Name),
      fitness_upto: cleanValue(fl.rc_fit_upto)
    }
  };
}

function formatDemoResponse(demoData, keyData, regNo) {
  return {
    status: true,
    demo_mode: true,
    source: "demo_fallback",
    api_info: { key_used: keyData.name, valid_till: keyData.expires, developer: DEVELOPER },
    owner_information: {
      owner_name: demoData.Owner_Name,
      father_name: demoData.Father_Name,
      mobile_number: "N/A (Demo Mode)",
      present_address: "N/A (Demo Mode)"
    },
    vehicle_details: {
      registration_number: demoData.Registration_Number,
      make: demoData.Make_Name,
      model: demoData.ModelName,
      color: demoData.Color,
      fuel_type: demoData.Fuel_Type,
      vehicle_class: demoData.Vehicle_Class,
      chassis_number: "DEMO" + regNo.slice(-6),
      engine_number: "DEMO" + regNo.slice(-6)
    },
    registration_details: {
      registration_date: demoData.Registration_Date,
      rto_name: "DEMO RTO",
      fitness_upto: "31-12-2025"
    },
    note: demoData.note || "Demo data - Real API unavailable"
  };
}

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Content-Type', 'application/json');
  
  if (req.method === 'OPTIONS') return res.status(200).end();
  
  let key = req.query.key || req.headers['api-key'];
  let regNo = req.query.Fuckreg || req.query.rc || req.query.reg_no;
  
  if (!key) {
    return res.status(400).json({ status: false, message: "API key missing. Use ?key=Introspection" });
  }
  
  if (!keys[key]) {
    return res.status(401).json({ status: false, message: "Invalid API key" });
  }
  
  const keyData = keys[key];
  const today = new Date().toISOString().split('T')[0];
  if (today > keyData.expires) {
    return res.status(403).json({ status: false, message: `Key expired on ${keyData.expires}` });
  }
  
  if (!regNo) {
    return res.status(400).json({ 
      status: false, 
      message: "Registration number missing", 
      example: "?key=Introspection&Fuckreg=GJ14X4555" 
    });
  }
  
  regNo = regNo.toUpperCase().trim();
  
  // Try APIs in order
  let apiResult = await tryUkraineAPI(regNo);
  if (!apiResult.success) {
    apiResult = await tryExternalAPI(regNo);
  }
  
  if (apiResult.success && apiResult.data) {
    return res.status(200).json(formatRealResponse(apiResult.data, keyData, regNo));
  }
  
  const demoData = getDemoVehicleData(regNo);
  return res.status(200).json(formatDemoResponse(demoData, keyData, regNo));
}
