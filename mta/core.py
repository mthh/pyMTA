# -*- coding: utf-8 -*-
"""
@author: mthh
"""
import pandas as pd
import igraph


def gdev(dataset, var1, var2, type_dev='rel', ref=None):
    ix1 = dataset.index
    data = dataset[[var1, var2]][
            (dataset[var1] != pd.np.NaN) & (dataset[var2] != pd.np.NaN)]
    if not ref:
        ref = data[var1].sum() / data[var2].sum()
    if 'rel' in type_dev:
        res = ((data[var1] / data[var2]) / ref) * 100
    elif 'abs' in type_dev:
        res = data[var1] - (ref * data[var2])
    else:
        raise Exception('')
    res = pd.DataFrame(index=ix1).join(pd.DataFrame(res))
    return res[0]


def tdev(dataset, var1, var2, key, type_dev='rel'):
    ix1 = dataset.index
    data = dataset[[var1, var2, key]][
            (dataset[var1] != pd.np.NaN) & (dataset[var2] != pd.np.NaN)]

    med = data.groupby([key], sort=False, as_index=False).sum()
    med['med'] = med[var1] / med[var2]
    tdev = pd.merge(data, med[[key, 'med']], on=key, how='left')

    if type_dev == 'rel':
        res = ((tdev[var1] / tdev[var2]) / tdev['med']) * 100
    elif type_dev == 'abs':
        res = tdev[var1] - (tdev[var2] * tdev['med'])
    else:
        raise Exception('')
    res = pd.DataFrame(index=ix1).join(pd.DataFrame(res))
    return res[0]


def sdev(gdf, var1, var2, type_dev, order=None, dist=None, mat=None):
    if order != None and dist != None:
        raise Exception('')
    if not order and not dist:
        raise Exception('')
    if not 'rel' in type_dev and not 'abs' in type_dev:
        raise Exception('')

    ix1 = gdf.index
    data = gdf[[var1, var2, 'geometry']][
            (gdf[var1] != pd.np.NaN) & (gdf[var2] != pd.np.NaN)]

    if not order:
        if not mat:
            mat = getMatDist(data)
        mat[mat <= dist] = 1
        mat[mat > dist] = 0

    elif not dist:
        mat = contiguityMat(data)
        mat[mat <= order] = 1
        mat[mat > order] = 0

    res = locmat(mat, data, var1, var2, type_dev)
    res = pd.DataFrame(index=ix1).join(pd.DataFrame(res))
    return res[0]


def locmat(mat, data, var1, var2, type_dev):
    mvar1 = mat * data[var1].values
    mvar2 = mat * data[var2].values

    if 'rel' in type_dev:
        r = (
            (data[var1] / data[var2]) / (mvar1.sum(axis=1) / mvar2.sum(axis=1))
            ) * 100
    elif 'abs' in type_dev:
        r = data[var1] - (data[var2] * mvar1.sum(axis=1) / mvar2.sum(axis=1))

    return r


def getMatDist(gdf):
    geoms = gdf.geometry.centroid
    n = len(geoms)
    mat = pd.np.zeros((n, n))
    for i, g1 in enumerate(geoms):
        for j, g2 in enumerate(geoms):
            mat[i,j] = g1.distance(g2)
    return mat


def matIntersects(gdf, tol=0):
    geoms = gdf.geometry
    n = len(geoms)
    mat = pd.np.zeros((n, n))
    if tol:
        for i, g1 in enumerate(geoms):
            for j, g2 in enumerate(geoms):
                mat[i,j] = g1.intersects(g2.buffer(tol))
    else:
        for i, g1 in enumerate(geoms):
            for j, g2 in enumerate(geoms):
                mat[i,j] = g1.intersects(g2)
    return mat


def contiguityMat(gdf):
    mat = matIntersects(gdf)
    g = igraph.Graph().Adjacency(mat.tolist())
    x = g.shortest_paths()
    return pd.np.array(x)

