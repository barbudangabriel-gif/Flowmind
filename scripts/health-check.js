import http from "http";

const endpoints = [
  { name: "API", url: "http://localhost:5174/fis/score" },
  { name: "UI", url: "http://localhost:5173" }
];

function check(url) {
  return new Promise(resolve => {
    const req = http.get(url, res => {
      let data = "";
      res.on("data", chunk => data += chunk);
      res.on("end", () => resolve({ status: res.statusCode, data }));
    });
    req.on("error", () => resolve({ status: 0, data: "" }));
    req.setTimeout(2000, () => {
      req.abort();
      resolve({ status: 0, data: "timeout" });
    });
  });
}

(async () => {
  for (const ep of endpoints) {
    const res = await check(ep.url);
    if (res.status === 200) {
      console.log(`✅ ${ep.name} OK (${ep.url})`);
      if (ep.name === "API") {
        try {
          const json = JSON.parse(res.data);
          if (typeof json.score === "number") {
            console.log(`   FIS Score: ${json.score}`);
          } else {
            console.log("   FIS Score missing in response!");
          }
        } catch {
          console.log("   API response not JSON!");
        }
      }
    } else {
      console.log(`❌ ${ep.name} FAIL (${ep.url}) [status: ${res.status}]`);
    }
  }
})();
