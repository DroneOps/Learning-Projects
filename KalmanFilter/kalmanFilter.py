from filterpy.kalman import ExtendedKalmanFilter
import numpy as np
import matplotlib.pyplot as plt

def Hx(x): # in this case the measurement function is linear, so we can just return the state
    return x

def HJacobian(x): # so the jacobian is just the identity matrix1
    return np.eye(2)
  
def sensor(t, std_dev): # simulation os a noisy sensor
    px = np.random.normal(np.cos(t),std_dev)
    py = np.random.normal(np.sin(t),std_dev)

    return px, py

def main():
    # initilize the kalman with 2 dimension in the input and in the state
    kalman = ExtendedKalmanFilter(dim_x=2,dim_z=2)
    kalman.P = np.eye(2)  # coovariance matrix
    kalman.x = np.array([[0],[0]]) # initial state

    # Noises matrices
    kalman.R = np.eye(2) * 2.0 # messurement noise
    kalman.Q = np.eye(2) * 0.2 # process noise

    t = np.arange(0,50,0.1) # time vector
    Noisy_pos_x = []
    Noisy_pos_y = []
    std_dev = 0.3 # standard deviation of the noise

    filtered = []

    for n in range(0,np.size(t)): 
        # state transition matrix in this case is the jacobian because our model is non linear.
        kalman.F = np.array([
                [-np.sin(t[n]),  0.0],
                [ 0.0,           np.cos(t[n])]
            ])
        
        px, py = sensor(t[n],std_dev) # simulate the sensor reading
        Noisy_pos_x.append(px)
        Noisy_pos_y.append(py)

        def my_predict_x(u=0): # overwrite the predict_x function to return the state transition function
            ''' In this case we need to do this becuse the filterpy library is designed for linear systems and non linear sensors, 
            so we need to overwrite the predict_x function with the non linear model. '''
            kalman.x = np.array([np.cos(t[n]), np.sin(t[n])])

        kalman.predict_x = my_predict_x # overwrite the predict_x 

        kalman.predict() # predict the state
        kalman.update(np.array([px, py]), # update the state with the linear measurement function and the jacobian of the measurement function
                              HJacobian=HJacobian, 
                              Hx=Hx)

        filtered.append(kalman.x[0].copy()) # we do a copy because the kalman.x is a reference to the state and we need to store the value of the state at this time step.

    noisyPos = np.array([Noisy_pos_x, Noisy_pos_y])


    # plot the results
    plt.plot(t, np.cos(t), color='green')
    plt.plot(t, noisyPos[0], color='red', linewidth=0.2)
    plt.plot(t, filtered, color='blue', linestyle='dashed', linewidth=1)
    plt.show()

if __name__ == '__main__':
    main()

