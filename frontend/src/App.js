import { Box } from '@mui/material';
import { IntegrationForm } from './integration-form';

function App() {
  return (
  <Box
    sx={{ 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      height: '100vh' 
    }}
  >
    <IntegrationForm />
  </Box>
  );
}

export default App;
