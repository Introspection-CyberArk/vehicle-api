// api/vehicle.js - Vehicle Registration Information API
// Owner: @Introspection007
// Version: 2.0

// ============================================
//   KEYS DATABASE - WITH YOUR CUSTOM KEY
// ============================================
const keys = {
  // 🔑 YOUR PERSONAL API KEY
  "Introspection": { 
    name: "Introspection", 
    expires: "2050-12-31",  // Valid until 31st December 2050
    plan: "LIFETIME",
    created_at: "2024-05-25"
  },
  
  // Existing keys (keep for compatibility)
  "Tushar1demo": { 
    name: "Tushar", 
    expires: "2026-05-25",
    plan: "PREMIUM"
  },
  
  "ukrainebst": { 
    name: "UkraineBST", 
    expires: "2026-05-25",
    plan: "PREMIUM"
  }
};

// Developer Information
const DEVELOPER = "@Introspection007";
const FREE_API = "https://t.me/exportbot01";
const EXTERNAL_API = "https://api.paanel.shop/api/gateway.php";

// ============================================
//   HELPER FUNCTIONS
// ============================================
function cleanValue(val) {
  if (!val || val === "" || val === "--" || val === null) return "N/A";
  return String(val);
}

// ============================================
//   MAIN HANDLER
// ============================================
export default async function handler(req, res) {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, API-Key, X-API-Key');
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }
  
  // Support both GET and POST
  let key = req.query.key || req.body?.key || req.headers['api-key'] || req.headers['x-api-key'];
  let regNo = req.query.Fuckreg || req.query.reg_no || req.query.rc || req.body?.Fuckreg || req.body?.reg_no;
  
  // ============================================
  //   VALIDATE API KEY
  // ============================================
  if (!key) {
    return res.status(400).json({
      status: false,
      message: "❌ API key missing. Use ?key=YOUR_KEY",
      example: "?key=Introspection&Fuckreg=GJ14X4555",
      free_api: FREE_API,
      developer: DEVELOPER
    });
  }
  
  if (!keys[key]) {
    return res.status(401).json({
      status: false,
      message: `❌ Invalid API key. Contact ${DEVELOPER} to get your key.`,
      valid_keys: Object.keys(keys),
      free_api: FREE_API,
      developer: DEVELOPER
    });
  }
  
  const keyData = keys[key];
  const expires = keyData.expires;
  const userName = keyData.name;
  const plan = keyData.plan || "STANDARD";
  
  // Check expiration
  const today = new Date().toISOString().split('T')[0];
  if (today > expires) {
    return res.status(403).json({
      status: false,
      message: `❌ Your API key expired on ${expires}. Please contact ${DEVELOPER} for a new key.`,
      expired_on: expires,
      free_api: FREE_API,
      developer: DEVELOPER
    });
  }
  
  // ============================================
  //   VALIDATE REGISTRATION NUMBER
  // ============================================
  if (!regNo) {
    return res.status(400).json({
      status: false,
      message: "❌ Registration number missing. Use ?Fuckreg=VEHICLE_NUMBER",
      example: `?key=${key}&Fuckreg=CH01CJ3944`,
      formats: ["GJ14X4555", "MH12AB1234", "DL8SCA1234", "UP32CD1234"],
      free_api: FREE_API,
      developer: DEVELOPER
    });
  }
  
  regNo = String(regNo).toUpperCase().trim();
  
  // Validate registration number format (Indian RC format)
  const rcPattern = /^[A-Z]{2}[0-9]{1,2}[A-Z]{1,2}[0-9]{4}$/;
  if (!rcPattern.test(regNo)) {
    return res.status(400).json({
      status: false,
      message: "❌ Invalid registration number format",
      example: "GJ14X4555, MH12AB1234, DL8SCA1234",
      provided: regNo,
      developer: DEVELOPER
    });
  }
  
  // ============================================
  //   CALL EXTERNAL API
  // ============================================
  const externalUrl = `${EXTERNAL_API}?key=Fuckedvehicle&Fuckreg=${encodeURIComponent(regNo)}`;
  
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 20000);
    
    const response = await fetch(externalUrl, {
      method: 'GET',
      signal: controller.signal,
      headers: {
        'User-Agent': 'Mozilla/5.0 (compatible; VehicleAPI/2.0)',
        'Accept': 'application/json'
      }
    });
    
    clearTimeout(timeoutId);
    
    if (!response.ok) {
      throw new Error(`External API returned ${response.status}`);
    }
    
    const data = await response.json();
    
    // Check if API returned success
    if (!data || !data.success || data.success !== true) {
      return res.status(404).json({
        status: false,
        message: "❌ Vehicle not found or invalid registration number.",
        reg_number: regNo,
        suggestion: "Try with: GJ14X4555, MH12AB1234, DL8SCA1234",
        free_api: FREE_API,
        developer: DEVELOPER
      });
    }
    
    // ============================================
    //   EXTRACT AND FORMAT DATA
    // ============================================
    const d = data.data || {};
    const fl = d.FastlaneResponse_Obj || {};
    
    const result = {
      status: true,
      
      // API Metadata
      api_info: {
        key_used: key,
        requested_by: userName,
        plan: plan,
        valid_till: expires,
        developer: DEVELOPER,
        free_api: FREE_API,
        timestamp: new Date().toISOString()
      },
      
      // --- Owner Information ---
      owner_information: {
        owner_name: cleanValue(d.Owner_Name),
        father_name: cleanValue(d.Father_Name),
        owner_serial: cleanValue(fl.rc_owner_sr),
        mobile_number: cleanValue(fl.rc_mobile_no),
        present_address: cleanValue(fl.rc_present_address),
        permanent_address: cleanValue(d.Permanent_Address),
        pincode: cleanValue(fl.pin_code)
      },
      
      // --- Vehicle Details ---
      vehicle_details: {
        registration_number: cleanValue(d.Registration_Number),
        make: cleanValue(d.Make_Name),
        model: cleanValue(d.ModelName),
        variant: cleanValue(d.Variant_Name),
        full_vehicle_name: cleanValue(fl.rc_maker_model),
        color: cleanValue(d.Color),
        fuel_type: cleanValue(d.Fuel_Type),
        vehicle_class: cleanValue(d.Vehicle_Class),
        vehicle_category: cleanValue(fl.rc_vch_catg),
        body_type: cleanValue(fl.rc_body_type_desc),
        seating_capacity: cleanValue(d.Seating_Capacity),
        manufacture_month_year: cleanValue(fl.rc_manu_month_yr),
        manufacture_year: cleanValue(d.Manufacture_Year),
        chassis_number: cleanValue(d.Chassis_Number),
        engine_number: cleanValue(d.Engin_Number),
        cubic_capacity: cleanValue(d.Cubic_Capacity),
        gross_vehicle_weight: cleanValue(fl.rc_gvw),
        unloaded_weight: cleanValue(fl.rc_unld_wt),
        wheelbase: cleanValue(fl.rc_wheelbase),
        no_of_cylinders: cleanValue(fl.rc_no_cyl),
        emission_norms: cleanValue(fl.rc_norms_desc)
      },
      
      // --- Registration Details ---
      registration_details: {
        registration_date: cleanValue(d.Registration_Date),
        registered_at: cleanValue(fl.rc_registered_at),
        rto_name: cleanValue(d.RTO_Name),
        rto_code: cleanValue(fl.rc_rto_code),
        rc_status: cleanValue(fl.rc_status),
        rc_status_as_on: cleanValue(fl.rc_status_as_on),
        fitness_upto: cleanValue(fl.rc_fit_upto),
        tax_upto: cleanValue(fl.rc_tax_upto),
        blacklist_status: cleanValue(fl.rc_blacklist_status),
        ncrb_status: cleanValue(fl.rc_ncrb_status),
        noc_details: cleanValue(fl.rc_noc_details)
      },
      
      // --- Insurance Details ---
      insurance_details: {
        insurance_company: cleanValue(d.Pyp_Insurer_Name),
        policy_number: cleanValue(d.Pyp_Policy_Number),
        insurance_expiry: cleanValue(d.Pyp_Policy_Expiry_Date),
        financer_name: cleanValue(fl.rc_financer)
      },
      
      // --- Permit Details ---
      permit_details: {
        permit_number: cleanValue(fl.rc_permit_no),
        permit_type: cleanValue(fl.rc_permit_type),
        permit_valid_from: cleanValue(fl.rc_permit_valid_from),
        permit_valid_upto: cleanValue(fl.rc_permit_valid_upto),
        permit_issue_date: cleanValue(fl.rc_permit_issue_dt)
      },
      
      // --- PUCC Details ---
      pucc_details: {
        pucc_number: cleanValue(d.Puc_Number),
        pucc_expiry: cleanValue(d.Puc_Expiry_Date)
      }
    };
    
    return res.status(200).json(result);
    
  } catch (error) {
    console.error('API Error:', error);
    
    if (error.name === 'AbortError') {
      return res.status(504).json({
        status: false,
        message: "⏰ Request timeout. Please try again.",
        free_api: FREE_API,
        developer: DEVELOPER
      });
    }
    
    return res.status(500).json({
      status: false,
      message: "❌ Server error: " + error.message,
      free_api: FREE_API,
      developer: DEVELOPER
    });
  }
}
