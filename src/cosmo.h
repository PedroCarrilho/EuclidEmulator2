#ifndef COSMOLOGY_H
#define COSMOLOGY_H
#include <gsl/gsl_integration.h>
//#include <gsl/gsl_interp.h>
#include <gsl/gsl_spline.h>

class Cosmology{
	public:	
		double cosmo[8], cosmo_tf[8], Omega_gamma_0, Omega_nu_0, rho_crit;

		/* Ranges for cosmological parameters */
        const double minima[8] = {0.04, 0.24, 0.00, 0.92, 0.61, -1.3, -0.7, 1.7e-9};
        const double maxima[8] = {0.06, 0.40, 0.15, 1.00, 0.73, -0.7, 0.7, 2.5e-9};
		
		/* Member functions */
		Cosmology(double Omega_b, double Omega_m, double Sum_m_nu, double n_s, double h, double w_0, double w_a, double A_s);
		~Cosmology();
		void read_from_file(char *filename);
		void print_cosmo();
		void print_cosmo_tf();
	    double compute_step_number(double z);	
		double rho_nu_i_integrand(double a, void *params);
		double a2t_integrand(double a, void *params);

	private:	
		/* Private members */
		const int nSteps, nTable;	
		double t0, t10, Delta_t, Neff, H0;

		gsl_integration_workspace *gsl_wsp;
		gsl_interp_accel *acc;
    	gsl_spline *z2nStep_spline;

		/* Private member functions*/
		void isoprob_tf();
		void check_parameter_ranges();
		void compute_z2nStep_spline();

		double Hubble(double a);
		double Omega_matter(double a);
		double Omega_gamma(double a);
		double Omega_nu(double a);
		double Omega_DE(double a);
		double a2t(double a);
		double a2Hubble(double a);
};

typedef struct {
            double mnu;
            double a;
            Cosmology * csm_instance;
} rho_nu_parameters;

static double rho_nu_i_integrand_wrapper(double p, void * pp){
    rho_nu_parameters *rho_nu_pars = reinterpret_cast<rho_nu_parameters *>(pp);
    return rho_nu_pars->csm_instance->rho_nu_i_integrand(p, rho_nu_pars);
}

typedef struct {
            Cosmology * csm_instance;
} a2t_parameters;

static double a2t_integrand_wrapper(double a, void *pp){
	a2t_parameters *a2t_pars = reinterpret_cast<a2t_parameters *>(pp);
    return a2t_pars->csm_instance->a2t_integrand(a, a2t_pars);
}
#endif
