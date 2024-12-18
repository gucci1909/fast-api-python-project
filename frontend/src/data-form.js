import { useState } from "react";
import {
  Box,
  TextField,
  Button,
  CircularProgress,
  Typography,
} from "@mui/material";
import axios from "axios";

const endpointMapping = {
  Notion: "notion",
  Airtable: "airtable",
  Hubspot: "hubspot",
};

export const DataForm = ({ integrationType, credentials }) => {
  const [loadedData, setLoadedData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const endpoint = endpointMapping[integrationType];

  const handleLoad = async () => {
    try {
      setIsLoading(true);

      const formData = new FormData();
      formData.append("credentials", JSON.stringify(credentials));
      let apiUrl = `http://localhost:8000/integrations/${endpoint}`;

      if (endpoint === "hubspot") {
        apiUrl += "/get_hubspot_items";
      } else {
        apiUrl += "/load";
      }

      const response = await axios.post(apiUrl, formData);
      const data = response.data;
      setIsLoading(false);
      setLoadedData(data);
    } catch (e) {
      alert(e?.response?.data?.detail);
      setIsLoading(false);
    }
  };

  return (
    <Box
      display="flex"
      justifyContent="center"
      alignItems="center"
      flexDirection="column"
      width="100%"
    >
      {isLoading && (
        <Box display="flex" justifyContent="center" alignItems="center" mb={2}>
          <CircularProgress />
        </Box>
      )}
      <Box display="flex" flexDirection="column" width="100%">
        <TextField
          label="Loaded Data"
          value={loadedData || ""}
          sx={{ mt: 2 }}
          InputLabelProps={{ shrink: true }}
          disabled
        />
        {!isLoading &&
          endpoint === "hubspot" &&
          loadedData?.map((item) => (
            <Box
              key={item.properties.hs_object_id}
              mt={2}
              p={2}
              sx={{ border: "1px solid #ccc", borderRadius: 4 }}
            >
              <Typography>
                <strong>Name:</strong> {item.properties.name || "N/A"}
              </Typography>
              <Typography>
                <strong>HS Object ID:</strong> {item.properties.hs_object_id}
              </Typography>
            </Box>
          ))}
        <Button onClick={handleLoad} sx={{ mt: 2 }} variant="contained">
          Load Data
        </Button>
        <Button
          onClick={() => setLoadedData(null)}
          sx={{ mt: 1 }}
          variant="contained"
        >
          Clear Data
        </Button>
      </Box>
    </Box>
  );
};
