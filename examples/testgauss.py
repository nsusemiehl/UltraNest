import argparse
import numpy as np
from numpy import log
import scipy.stats

def main(args):
    ndim = args.x_dim
    sigma = args.sigma
    width = max(0, 1 - 5 * sigma)
    centers = (np.sin(np.arange(ndim)/2.) * width + 1.) / 2.
    centers = np.ones(ndim) * 0.5

    def loglike(theta):
        like = -0.5 * (((theta - centers)/sigma)**2).sum(axis=1) - 0.5 * np.log(2 * np.pi * sigma**2) * ndim
        return like

    def transform(x):
        return x
    
    import string
    paramnames = list(string.ascii_lowercase)[:ndim]
    
    if args.pymultinest:
        from pymultinest.solve import solve
        
        def flat_loglike(theta):
            return loglike(theta.reshape((1, -1)))
        
        result = solve(LogLikelihood=flat_loglike, Prior=transform, 
            n_dims=ndim, outputfiles_basename=args.log_dir + 'MN-%dd' % ndim,
            verbose=True, resume=True, importance_nested_sampling=False)
        
        print()
        print('evidence: %(logZ).1f +- %(logZerr).1f' % result)
        print()
        print('parameter values:')
        for name, col in zip(paramnames, result['samples'].transpose()):
            print('%15s : %.3f +- %.3f' % (name, col.mean(), col.std()))
    
    elif args.reactive:
        from mininest import ReactiveNestedSampler
        sampler = ReactiveNestedSampler(paramnames, loglike, transform=transform, 
            min_num_live_points=args.num_live_points,
            log_dir=args.log_dir + 'RNS-%dd' % ndim, append_run_num=True,
            draw_multiple=False)
        sampler.run(frac_remain=0.5, min_ess=400)
        sampler.print_results()
        sampler.plot()
    else:
        from mininest import NestedSampler
        sampler = NestedSampler(paramnames, loglike, transform=transform, 
            num_live_points=args.num_live_points,
            log_dir=args.log_dir + '-%dd' % ndim, append_run_num=True)
        sampler.run()
        sampler.print_results()
        sampler.plot()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--x_dim', type=int, default=2,
                        help="Dimensionality")
    parser.add_argument("--num_live_points", type=int, default=1000)
    parser.add_argument('--sigma', type=float, default=0.01)
    parser.add_argument('--run_num', type=str, default='')
    parser.add_argument('--log_dir', type=str, default='logs/loggauss')
    parser.add_argument('--reactive', action='store_true')
    parser.add_argument('--pymultinest', action='store_true')

    args = parser.parse_args()
    main(args)
