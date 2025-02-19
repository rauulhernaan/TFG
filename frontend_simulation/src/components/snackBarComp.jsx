import React, { createContext, useContext, useState } from 'react';
import Snackbar from '@mui/material/Snackbar';
import MuiAlert from '@mui/material/Alert';
import Slide from '@mui/material/Slide';

const SnackbarContext = createContext(null);

const Alert = React.forwardRef(function Alert(props, ref) {
    return <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />;
});
  
function SlideTransition(props) {
      return <Slide {...props} direction="left" />;
    }


export const SnackbarProvider = ({ children }) => {
    const [open, setOpen] = useState(false);
    const [message, setMessage] = useState('');
    const [severity, setSeverity] = useState('success');
    const vertical = 'top'
    const horizontal = 'right'
    

    const handleClose = (event, reason) => {
        if (reason === 'clickaway') {
            return;
        }
        setOpen(false);
    };

    const showSnackbar = (msg, severity = 'success') => {
        setMessage(msg);
        setSeverity(severity);
        setOpen(true);
    };

    return (
        <SnackbarContext.Provider value={showSnackbar}>
            {children}
            <Snackbar open={open} autoHideDuration={2000} onClose={handleClose} TransitionComponent={SlideTransition} anchorOrigin={{ vertical, horizontal }}>
                <Alert onClose={handleClose} severity={severity} sx={{ width: '100%' }}>
                    {message}
                </Alert>
            </Snackbar>
        </SnackbarContext.Provider>
    );
};

export const useSnackbar = () => {
    return useContext(SnackbarContext);
};