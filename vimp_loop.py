import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression


class vimp:
    def get_vimp(self, y, x, d):
        self.y = y
        self.x = x
        self.d = d
        poly = PolynomialFeatures(degree=self.d)
        X_poly = poly.fit_transform(self.x)

        model = LinearRegression()
        model.fit(X_poly, self.y)
        u = model.predict(X_poly)

        nvar = self.x.shape[1]
        psi = [0] * nvar
        mu = [0] * nvar

        for i in range(nvar):
            # Create a new subset of x by deleting one column
            X_sub = np.delete(self.x, i, axis=1)
            # Apply PolynomialFeatures to the new subset
            poly_sub = PolynomialFeatures(degree=self.d)
            X_sub_poly = poly_sub.fit_transform(X_sub)

            # Fit a new model on the transformed subset
            model_sub = LinearRegression()
            model_sub.fit(X_sub_poly, self.y)
            u_sub = model_sub.predict(X_sub_poly)

            # Calculate mu using the coefficients from the new model
            mu[i] = u_sub

            # Calculate variance explained for each model
            residual_var = np.mean((self.y - u) ** 2)
            mu_var = np.mean((self.y - mu[i]) ** 2)
            psi[i] = 1 - (residual_var / np.var(self.y)) - (1 - (mu_var / np.var(self.y)))

        return psi

    def datasplit(self, q):
        self.q = q
        # Splitting data
        y1 = self.y[:int(len(self.x) / 2)]
        y2 = self.y[int(len(self.x) / 2):]

        X1 = self.x[:int(len(self.x) / 2)]
        X2 = self.x[int(len(self.x) / 2):]

        # Estimating psi1 and psi2
        v1 = self.get_vimp(y1, X1, self.d)
        v2 = self.get_vimp(y2, X2, self.d)

        psi1 = np.array(v1)
        psi2 = np.array(v2)

        # Calculate mirror stat
        m = abs(psi1 + psi2) - abs(psi1 - psi2)

        # Designate FDR level
        # Assuming M contains p-values from multiple hypothesis tests
        q = self.q  # Your designated FDR level

        # Sort the mirror statistics in ascending order
        sorted_m = np.sort(m)
        n = len(sorted_m)

        # Calculate the cutoff tau_q using BH procedure
        tau_q = 0
        for i, t in enumerate(sorted_m):
            # Calculate the critical value for this p-value
            critical_value = (i + 1) / n * q

            # Find the largest p-value where the p-value is less than the critical value
            if t <= critical_value:
                tau_q = t

        print("tau_q:", tau_q)
