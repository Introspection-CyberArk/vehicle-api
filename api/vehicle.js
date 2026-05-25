// api/vehicle.js - Integrated with Ukraine API + Demo Fallback
// Developer: @Introspection007

const keys = {
  "Introspection": { name: "Introspection", expires: "2050-12-31", plan: "LIFETIME" },
  "Tushar1demo": { name: "Tushar", expires: "2026-05-25" },
  "ukrainebst": { name: "UkraineBST", expires: "2026-05-25" }
};

const DEVELOPER = "@Introspection007";
const FREE_API = "https://t.me/exportbot01";

// 🔑 PRIMARY API (Ukraine Vehicle API - Working)
const UKRAINE_API = "https://ukrainexinfo-vehicle-advance.42web.io/gateway.php";
const UKRAINE_KEY = "Tushar1demo";  // Their API key

// 🔄 FALLBACK: Your original external API (if needed)
const EXTERNAL_API = "https://api.paanel.shop/api/gateway.php";

function cleanValue(val) {
  if (!val || val === "" || val === "--" || val === null) return "N/A";
  return String(val);
}

// ============================================
// DEMO VEHICLE DATABASE (Fallback)
// ============================================
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
    },
    "DL8SCA1234": {
      Owner_Name: "PRIYA SINGH", Father_Name: "VIKRAM SINGH",
      Registration_Number: "DL8SCA1234", Make_Name: "HYUNDAI",
      ModelName: "I20 SPORTZ", Color: "STARRY NIGHT",
      Fuel_Type: "DIESEL", Vehicle_Class: "FOUR WHEELER",
      Registration_Date: "10-06-2021", Cubic_Capacity: "1493 CC"
    },
    "CH01CJ3944": {
      Owner_Name: "CHANDIGARH OWNER", Father_Name: "TEST USER",
      Registration_Number: "CH01CJ3944", Make_Name: "TEST VEHICLE",
      ModelName: "DEMO MODEL", Color: "WHITE",
      Fuel_Type: "PETROL", Vehicle_Class: "FOUR WHEELER",
      Registration_Date: "01-01-2023", Cubic_Capacity: "N/A"
    }
  };
  
  if (demoDB[regNo]) return { ...demoDB[regNo], demo_mode: true };
  
  return {
    Owner_Name: `OWNER OF ${regNo}`,
    Father_Name: "REGISTERED OWNER",
    Registration_Number: regNo,
    Make_Name: regNo.startsWith("DL") ? "MARUTI" : regNo.startsWith("MH") ? "HYUNDAI" : "HONDA",
    ModelName: "STANDARD MODEL",
    Color: ["BLACK", "WHITE", "RED", "BLUE", "SILVER"][Math.floor(Math.random() * 5)],
    Fuel_Type: Math.random() > 0.7 ? "DIESEL" : "PETROL",
    Vehicle_Class: regNo.length === 10 ? "FOUR WHEELER" : "TWO WHEELER",
    Registration_Date: "01-01-2023",
    Cubic_Capacity: "N/A",
    demo_mode: true,
    note: "Auto-generated demo data"
  };
}

// ============================================
// TRY UKRAINE API FIRST
// ============================================
async function tryUkraineAPI(regNo) {
  try {
    const controller = new AbortController();
    setTimeout(() => controller.abort(), 10000);
    
    const url = `${UKRAINE_API}?key=${UKRAINE_KEY}&Fuckreg=${encodeURIComponent(regNo)}`;
    console.log("Trying Ukraine API:", url);
    
    const response = await fetch(url, {
      signal: controller.signal,
      headers: { 
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json'
      }
    });
    
    if (response.ok) {
      const data = await response.json();
      // Check if API returned success (status === true) OR has vehicle data
      if (data && (data.status === true || data.status === "true")) {
        console.log("Ukraine API returned real data!");
        return { success: true, data: data };
      } else if (data && data.status === "false") {
        console.log("Ukraine API: Vehicle not found in their DB");
        return { success: false, message: data.message };
      }
    }
  } catch (error) {
    console.log("Ukraine API failed:", error.message);
  }
  return { success: false, message: "API request failed" };
}

// ============================================
// FALLBACK: TRY ORIGINAL EXTERNAL API
// ============================================
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

// ============================================
// FORMAT REAL API RESPONSE
// ============================================
function formatRealResponse(apiData, keyData, regNo) {
  // Handle Ukraine API response format
  let d = apiData.data || apiData;
  let fl = d.FastlaneResponse_Obj || {};
  
  // If Ukraine API returns different structure
  if (apiData.owner_information) {
    return {
      status: true,
      source: "ukraine_api",
      api_info: { key_used: keyData.name, valid_till: keyData.expires, developer: DEVELOPER },
      owner_information: apiData.owner_information || {},
      vehicle_details: apiData.vehicle_details || {},
      registration_details: apiData.registration_details || {}
    };
  }
  
  return {
    status: true,
    source: "external_api",
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

// ============================================
// FORMAT DEMO RESPONSE
// ============================================
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
    note: demoData.note || "Using demo data - Real API returned no results"
  };
}

// ============================================
// MAIN HANDLER
// ============================================
export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Content-Type', 'application/json');
  
  if (req.method === 'OPTIONS') return res.status(200).end();
  
  let key = req.query.key || req.headers['api-key'];
  let regNo = req.query.Fuckreg || req.query.rc || req.query.reg_no;
  
  // Validate API key
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
  
  // ============================================
  // TRY APIs IN ORDER: Ukraine → External → Demo
  // ============================================
  
  // 1. Try Ukraine API first
  let apiResult = await tryUkraineAPI(regNo);
  
  // 2. If Ukraine failed, try External API
  if (!apiResult.success) {
    apiResult = await tryExternalAPI(regNo);
  }
  
  // 3. If real API returned data, format and send
  if (apiResult.success && apiResult.data) {
    return res.status(200).json(formatRealResponse(apiResult.data, keyData, regNo));
  }
  
  // 4. Final fallback: Demo data
  const demoData = getDemoVehicleData(regNo);
  return res.status(200).json(formatDemoResponse(demoData, keyData, regNo));
}
