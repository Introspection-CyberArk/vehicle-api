// api/vehicle.js - Fixed version with demo fallback
const keys = {
  "Introspection": { name: "Introspection", expires: "2050-12-31", plan: "LIFETIME" },
  "Tushar1demo": { name: "Tushar", expires: "2026-05-25" },
  "ukrainebst": { name: "UkraineBST", expires: "2026-05-25" }
};

const DEVELOPER = "@Introspection007";
const FREE_API = "https://t.me/exportbot01";
const EXTERNAL_API = "https://api.paanel.shop/api/gateway.php";

function cleanValue(val) {
  if (!val || val === "" || val === "--" || val === null) return "N/A";
  return String(val);
}

// Demo vehicle database
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
    Owner_Name: "DEMO OWNER", Father_Name: "DEMO FATHER",
    Registration_Number: regNo, Make_Name: "DEMO VEHICLE",
    ModelName: "STANDARD MODEL", Color: "UNKNOWN",
    Fuel_Type: "PETROL", Vehicle_Class: "FOUR WHEELER",
    Registration_Date: "01-01-2023", Cubic_Capacity: "N/A",
    demo_mode: true, message: "Demo data - External API blocked (403)"
  };
}

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
    return res.status(400).json({ status: false, message: "Registration number missing", example: "?key=Introspection&Fuckreg=GJ14X4555" });
  }
  
  regNo = regNo.toUpperCase().trim();
  
  // Try external API first
  try {
    const controller = new AbortController();
    setTimeout(() => controller.abort(), 10000);
    
    const response = await fetch(`${EXTERNAL_API}?key=Fuckedvehicle&Fuckreg=${encodeURIComponent(regNo)}`, {
      signal: controller.signal,
      headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36' }
    });
    
    if (response.ok) {
      const data = await response.json();
      if (data && data.success === true) {
        return res.status(200).json(formatResponse(data, keyData, regNo));
      }
    }
  } catch (error) {
    console.log("External API failed, using demo data:", error.message);
  }
  
  // Fallback to demo data
  const demoData = getDemoVehicleData(regNo);
  return res.status(200).json(formatDemoResponse(demoData, keyData, regNo));
}

function formatResponse(data, keyData, regNo) {
  const d = data.data || {};
  const fl = d.FastlaneResponse_Obj || {};
  
  return {
    status: true,
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
    note: "⚠️ Using demo data - External API is currently unavailable (403 error)"
  };
}
